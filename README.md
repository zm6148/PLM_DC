# PLM data challegne

> Prediction on test data results can be visulized here: [Web app address](http://dataengineermz.club/)

## Table of Contents

1. [Usage](README.md#Usage)
1. [System](README.md#System)
1. [Setup](README.md#setup)
1. [Run the system](README.md#run-the-system)
1. [Contact Information](README.md#contact-information)

***

## Summaty

For this data challege, I tried to answer the following 2 questions:
1. Can the deteration speed be predicted based on the user's exsiting condtions?
2. Can the medical condtions be predicted based on the user's reported symptoms?

Idealy, I would want to link those questions together. However, in the data I was given, there are only 16 common user_ids between user_ALSFRS_score data and user_symptom data, too few to train models that can relaybley link those two. I chose the above 2 questions instead.

For both questions, I seprated user ids into training ids and testing ids. All models were developed using data associated with training user ids only(177 users for question 1, 29458 for question 2). The model will only see the data from testing id when using the Web App.

---
## Methods and Results

For question 1, where I want to predict deetration speed based on user's existing condition. I defined the deetarion speed as the slop of the linear fit of idndividual user's ALSFRS score. I built a general linear model (GLM) using user conditions to build the regression matrix: 20 unique conditions, each conditon as a columnm of 0 and 1s, with 1s marking the presence of one condition (177 * 20 matrix). The trained model was used on tesing user ids to predict the slop on an indivual user bases. 

For all data from testing user ids, the results is shown below
![q1_png](./test_scripts/q1.png)

For question 1, where I want to medical condtions be predicted based on the user's reported symptoms. There are 6536 unique symtoms in the dataset. Similar method as question 1 was used to build training data set, a matrix consisited of symtom svertivy score (15591 * 300 matrix) was used to encode symtopms for each user. I only picked top 300 most common symptoms to train a Decision Tree Classifier with 250 tree stumps caped at 175 deepth trained in sequence. This classifier was trained on users with only 1 condtions, thus can only predict 1 conditons even though test user may have multiple conditions

When tested on data accosicated with testing user ids, the accuracy is 68%. The detials results are shown below![system_png](./img/ezgif.com-video-to-gif(2).gif)
![q2_png](./test_scripts/q2.png)

---
## Instruction

df

---
## If I had more time


## Contact Information

* [LinkedIn](https://www.linkedin.com/in/zm6148)
* mz86@njit.edu


