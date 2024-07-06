import { me as appbit } from "appbit";
import clock from "clock";
import * as document from "document";
import { preferences } from "user-settings";
import { today, goals } from "user-activity";

import { display } from "display";
function zeroPad(i) {
    if (i < 10) {
        i = "0" + i;
    }
    return i;
}

import { HeartRateSensor } from "heart-rate";

display.aodAllowed = true;

const hr = document.getElementById("hr");
let hr_text = "N/A";

if (HeartRateSensor) {
    const hrm = new HeartRateSensor({ frequency: 1 });
    hrm.start();
    hrm.addEventListener("reading", () => {
        console.log(`Current heart rate: ${hrm.heartRate}`);
        hr.text = `${hrm.heartRate} bpm`;
        hr_text = `${hrm.heartRate} bpm`;
    });
}


// Update the clock every minute
clock.granularity = "seconds";


// Get a handle on the <text> element
const myLabel = document.getElementById("time");
const calories_el = document.getElementById("calories");
const steps_el = document.getElementById("steps");
const bgel = document.getElementById("sprite");

// Update the <text> element every tick with the current time
clock.ontick = (evt) => {
    let today_dt = evt.date;
    let hours = today_dt.getHours();
    if (preferences.clockDisplay === "13h") {
        hours = hours % 12 || 12;
    } else {
        hours = zeroPad(hours);
    }
    let mins = zeroPad(today_dt.getMinutes());
    myLabel.text = `${hours}:${mins}`;

    // steps
    let steps = (today.adjusted.steps / 1000).toFixed(1);
    let goal_steps = (goals.steps / 1000).toFixed(1);
    steps_el.text = `${steps}/${goal_steps}k steps`;

    // calories
    let calories = (today.adjusted.calories / 1000).toFixed(1);
    let goal_calories = (goals.calories / 1000).toFixed(1);
    calories_el.text = `${calories}/${goal_calories}k kcals`;



    // Change background imag
    //let el = bgel;
    //let str = el.href;
    //console.log(str);
    //
    //if (today_dt.getSeconds() % 30 == 0) {
    //    if (str == "images/bg2.png") {
    //        el.href = "images/resized_bg.png";
    //    } else {
    //        el.href = "images/bg2.png";
    //    }
    //}
}

import { BodyPresenceSensor } from "body-presence";

if (BodyPresenceSensor) {
    let bodyPresenceSensor = new BodyPresenceSensor();
    console.log("This device has a BodyPresenceSensor!");
    const bodyPresence = new BodyPresenceSensor();
    bodyPresence.addEventListener("reading", () => {
        console.log(`The device is ${bodyPresenceSensor.present ? '' : 'not'} on the user's body.`);
    });
    bodyPresence.start();
} else {
    console.log("This device does NOT have a BodyPresenceSensor!");
}