export const BUILDINGS_PAINT = {
  'fill-extrusion-color': '#333',

// use an 'interpolate' expression to add a smooth transition effect to the
// buildings as the user zooms in
  'fill-extrusion-height': [
    'interpolate',
    ['linear'],
    ['zoom'],
    15,
    0,
    15.05,
    ['get', 'height']
  ],
  'fill-extrusion-base': [
    'interpolate',
    ['linear'],
    ['zoom'],
    15,
    0,
    15.05,
    ['get', 'min_height']
  ],
  'fill-extrusion-opacity': 0.6
}
