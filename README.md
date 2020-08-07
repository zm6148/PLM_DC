# PLM data challegne

> [App address](https://www.dataengineermz.club)

## Table of Contents

1. [Summary](README.md#Usage)
1. [Methods](README.md#System)
1. [Instruction](README.md#setup)
1. [Contact Information](README.md#contact-information)

***

## Usage

This project aims to provide users the live update of traffic patterns (detailed counts of different types of vehicles at major junctions). This information would be useful to daily commuters and add to currently available traffic speed data for traffic planners.

In addition to live updates, this project also records historical data.
- Historical traffic counts at all junctions (last hour, day, week).
- Detailed traffic breakdown at user selected junctions (last hour, day, week).

![Demo_gif](./img/ezgif.com-video-to-gif(1).gif)

For example the traffic condition along I-95 in Bronx NY.

---
## System

This data pipeline takes in live video streams from traffic cams and dedicates 1 computing resource (t2.medium) performing data extraction using computer vision (neural net implemented in OpenCV) analysis for 4 traffic cam footages. After the data extraction stage, the extracted traffic information is fed to a Kafka data stream for temporary storage and queuing. A kafka consumer aggregates the data and saves it to a database. The flask front end displays the data in real-time.

![system_png](./img/ezgif.com-video-to-gif(2).gif)


---
## Setup

This pipeline requires 16 AWS EC2s. [Pegasus](https://github.com/InsightDataScience/pegasus) was used to set up multiple EC2s easier.

For each EC2, clone this repository

```
git clone https://github.com/zm6148/2020_insight_de_traffic.git
```
and run the requiements.sh to install required technologies.

```
bash requirements.sh
```


## Start the pipline

#### Strat data analysis EC2
At each 14 data extraction EC2s
```
python3 2020_insight_de_traffic/kafka_producer/src/multi_kafka_producer_3_cams.py &
```
#### Strat kafka consumer EC2
At kakfa consumer EC2
```
python3 2020_insight_de_traffic/dash/src/msk_consumer_save_direct.py &
```
#### Strat front end EC2
At front end EC2
```
python3 2020_insight_de_traffic/dash/src/app_database_v2.py &
```

## Contact Information

* [LinkedIn](https://www.linkedin.com/in/zm6148)
* mz86@njit.edu


