import React from 'react';
import ReactMapboxGl, {Layer, Feature, ZoomControl, ScaleControl, RotationControl, MapContext} from 'react-mapbox-gl';
import mapboxgl from 'mapbox-gl';
import { length as turfLength } from '@turf/turf';
import { lineString } from '@turf/helpers';
import 'mapbox-gl/dist/mapbox-gl.css';

import api from "../../api";
import {lerp, lerpCoord} from "../../utils/animation";
import {MAP_COLLECTION, MAP_CENTER} from "../../consts";
import {addDate} from "../../utils/date";
import {TimeContext} from "../TimeController";

import styles from './style.module.scss';
import {BUILDINGS_PAINT} from "../../utils/mapbox-paint";

const center = MAP_CENTER
// const center = [0, 0]

const Map = ReactMapboxGl({
    accessToken: process.env.REACT_APP_MAPBOX_API_KEY,
    dragRotate: false,
    pitchWithRotate: false,
});

const ROUTE_DATA_LIMIT = 1000
const ROUTE_MAX_DISTANCE = 100000
const ROUTE_LOAD_TIME_SPAN = 15 * 1000  // 60s

const POSITION_CIRCLE_PAINT = {
    'circle-stroke-width': 1,
    'circle-radius': 2.5,
    'circle-blur': 0.15,
    // 'circle-color': '#3770C6',
    'circle-color': [
        "interpolate",
        ["linear"],
        ["get", "speed"],
        0, "#210000",
        10, "#5b0202",
        20, "#ee0202",
        40, "#eec702",
        60, "#55ee02",
        150, "#c7ffa8",
],
    'circle-stroke-color': 'white'
};

const CAR_LAYER_NAME = 'car-marker';

const isRouteShowing = (route, now) =>
    route.start <= new Date(now) &&
    addDate(route.start, route.route.length * 1000) > new Date(now)

const calcCarSpeed = (timeFromStart, route) => {
    const coords = route.route;
    const getSpeedByKmh = (a, b) => {
        const line = lineString([a, b]);
        const length = turfLength(line);
        return length * 60 * 60;
    }
    if (coords.length < 2) return 0;
    const playSpeed = 1;
    const nowIndex = Math.floor(timeFromStart);
    const duration = (timeFromStart - nowIndex) / playSpeed;
    const before = nowIndex > 0 ? getSpeedByKmh(coords[nowIndex - 1], coords[nowIndex]) : route.initSpeed;
    const after = nowIndex + 1 < coords.length ? getSpeedByKmh(coords[nowIndex], coords[nowIndex + 1]) : route.lastspeed;
    return lerp(before, after, duration);
}

class CarRouteMap extends React.Component {
    // static propTypes = {
    //     timeController: TimeController
    // };

    hasInit = false

    state = {
        center,
        // routes: {},
        routes: [],
        lastLoadTime: null,
    }

    updateLock = false
    lastTickTime = null

    constructor(props) {
        super(props);
        const { timeController } = props;
        this.state.lastLoadTime = timeController.getStartTime();
    }

    componentDidMount() {
        const { timeController } = this.props;
        timeController.register(params => this.onTick(params))
        this._loadInitData(center[0], center[1], timeController.getStartTime());
    }

    async _loadInitData(lng, lat, time) {
        time = new Date(time)
        const data = await api.loadNearRoute({
            lng, lat,
            startTime: time,
            endTime: addDate(time, ROUTE_LOAD_TIME_SPAN),
            collection: MAP_COLLECTION,
            limit: ROUTE_DATA_LIMIT,
            max: ROUTE_MAX_DISTANCE,
        })
        console.log(`load init route data (${lng}, ${lat}, ${time}):`, data)
        // const routes = transRouteArray2Dict(data)
        const routes = data
        this.setState({ routes, lastLoadTime: time })
        this.clean()
        // setImmediate(() => this.play())
    }

    async _loadUpdatedData(lng, lat, time) {
        time = new Date(time)
        if (this.updateLock) {
            // console.debug("meet update lock:", lng, lat, time)
            return
        }
        this.updateLock = true
        const data = await api.loadNearRoute({
            lng, lat,
            startTime: time,
            endTime: addDate(time, ROUTE_LOAD_TIME_SPAN),
            collection: MAP_COLLECTION,
            limit: ROUTE_DATA_LIMIT,
            max: ROUTE_MAX_DISTANCE,
        })
        console.log(`update route data (${lng}, ${lat}, ${time}):`, data)
        const routes = data

        this.updateLock = false


        this.setState(({routes: oldRoutes, lastLoadTime, center}) => {
            let updated = { routes: [...oldRoutes, ...routes] }
            if (lastLoadTime < time
                && center[0] === lng
                && center[1] === lat
            ) {
                updated.lastLoadTime = time
            }
            return updated
        })

        this.clean()
    }

    clean() {
        let { routes, lastLoadTime } = this.state
        const { timeController } = this.props
        const now = timeController.getNow()
        const before = routes.length
        routes = routes.filter(r =>
            r.start.getTime() + r.route.length * 1000 >= now ||
            r.start.getTime() < Math.max(now, lastLoadTime.getTime() + ROUTE_LOAD_TIME_SPAN)
        );
        const after = routes.length
        console.log(`clean ${before - after} routes`)
        this.setState({routes})
    }

    // timestamp是从0开始算的，基础单位为ms，小数点后还有3位
    onTick({ now }) {
        const { lastLoadTime, center } = this.state
        const restTime = lastLoadTime.getTime() - now
        if (restTime <= ROUTE_LOAD_TIME_SPAN) {
            // debugger
           this._loadUpdatedData(center[0], center[1], addDate(lastLoadTime, ROUTE_LOAD_TIME_SPAN))
        }
        // console.debug("on tick", timestamp, deltaTime)
        // 在有bearing的时候，在requestAnimationFrame使用setState会导致地图无法操作，可能和setState的异步属性有关
    }

    render() {
        const { onMoved } = this.props
        const { routes } = this.state
        // console.debug("rerendering")
        return (
            <div className={styles.mapWrapper}>
                <TimeContext.Consumer>
                    {({ now }) => (
                        <Map
                            // eslint-disable-next-line
                            style="mapbox://styles/mapbox/dark-v10"
                            // style="mapbox://styles/mapbox/streets-v9"
                            containerStyle={{
                                height: '100%',
                                width: '100%'
                            }}
                            center={center}
                            onDrag={(map, event) => {
                                console.log("on drag", map, event)
                                // console.log(map.getCenter().wrap())
                                // console.dir(event)
                                onMoved && onMoved(map.getCenter().wrap())

                            }}
                            onDragEnd={(map, event) => {
                                const center = map.getCenter().wrap();
                                console.log("on drag end", map, event, center)
                                this.setState({
                                    center: [center.lng, center.lat]
                                })
                                setImmediate(() => this._loadInitData(center.lng, center.lat, now))
                            }}
                            pitch={[45]}
                            // bearing={[-17.6]}
                            dragRotate={false}
                            pitchWithRotate={false}
                            // antialias={true}
                        >
                            <MapContext.Consumer>
                                {(map) => {

                                    // Create a popup, but don't add it to the map yet.
                                    const popup = new mapboxgl.Popup({
                                        closeButton: false,
                                        closeOnClick: false
                                    });

                                    map.on('mouseenter', CAR_LAYER_NAME, function (e) {
                                        // Change the cursor style as a UI indicator.
                                        map.getCanvas().style.cursor = 'pointer';

                                        const coordinates = e.features[0].geometry.coordinates.slice();
                                        const description = e.features[0].properties.description;

                                        // Ensure that if the map is zoomed out such that multiple
                                        // copies of the feature are visible, the popup appears
                                        // over the copy being pointed to.
                                        while (Math.abs(e.lngLat.lng - coordinates[0]) > 180) {
                                            coordinates[0] += e.lngLat.lng > coordinates[0] ? 360 : -360;
                                        }

                                        // Populate the popup and set its coordinates
                                        // based on the feature found.
                                        popup.setLngLat(coordinates).setHTML(description).addTo(map);
                                    });

                                    map.on('mouseleave', CAR_LAYER_NAME, function () {
                                        map.getCanvas().style.cursor = '';
                                        popup.remove();
                                    });
                                }}
                            </MapContext.Consumer>
                            <Layer
                                type="circle"
                                id={CAR_LAYER_NAME}
                                // layout={{ 'icon-image': 'marker-15' }}
                                paint={POSITION_CIRCLE_PAINT}
                            >
                                {
                                    routes
                                        .filter(route => isRouteShowing(route, now)).map(route => {
                                            const frameTime = Math.floor(now / 1000);
                                            const start = Math.floor(route.start / 1000);
                                            const nowIndex = frameTime - start;
                                            const coords = route.route;
                                            const speed = calcCarSpeed((now - route.start.getTime()) / 1000, route)
                                            const coord = nowIndex > 0 ? lerpCoord(coords[nowIndex - 1], coords[nowIndex], now / 1000 - frameTime)  : coords[nowIndex]

                                            const description = `
                                                <p>
                                                    name: ${route.name}
                                                    <br />
                                                    speed: ${speed.toFixed(2)}
                                                    <br />
                                                    coord: ${coord[0].toFixed(4)}, ${coord[1].toFixed(4)}
                                                </p>
                                            `

                                            return (
                                                <Feature
                                                    coordinates={coord}
                                                    properties={{ speed, description }}
                                                    key={route.name}
                                                />
                                            )
                                    }
                                    )
                                }
                            </Layer>
                            <Layer
                                id="3d-buildings"
                                type="fill-extrusion"
                                sourceId="composite"
                                sourceLayer="building"
                                filter={['==', 'extrude', 'true']}
                                paint={BUILDINGS_PAINT}
                            />
                            <ZoomControl />
                            <ScaleControl />
                            <RotationControl />
                        </Map>
                    )}
                </TimeContext.Consumer>
            </div>
        );
    }
}

export default CarRouteMap;
