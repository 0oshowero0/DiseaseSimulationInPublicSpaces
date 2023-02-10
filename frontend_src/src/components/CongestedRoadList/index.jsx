import React from 'react';
import styles from './style.module.scss';

class CongestedRoadList extends React.Component {
  render() {
    return (
      <div className={styles.congestedRoadList}>
        <h1>常发拥堵路段</h1>
      </div>
    )
  }
}

export default CongestedRoadList
