import React from 'react';
import styles from "./style.module.scss";
import AirportScene from "../../components/InDoorEmulator/AirportScene";

function InDoorPage() {
  return (
    <div className={styles.inDoorPageContainer}>
      <AirportScene />
    </div>
  )
}

export default InDoorPage;
