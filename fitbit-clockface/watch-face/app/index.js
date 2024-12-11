import clock from "clock";
import * as document from "document";
import { preferences } from "user-settings";
import { today, goals } from "user-activity";
import { BodyPresenceSensor } from "body-presence";
import { HeartRateSensor } from "heart-rate";
import { display } from "display";

function zeroPad(i) {
    if (i < 10) {
        i = "0" + i;
    }
    return i;
}
display.aodAllowed = true;

let root = document.getElementById('root');
const screenWidth = root.width;

const hr = document.getElementById("hr");
let hr_text = "N/A";

if (HeartRateSensor) {
    const hrm = new HeartRateSensor({ frequency: 1 });
    hrm.start();
    hrm.addEventListener("reading", () => {
        hr.text = `${hrm.heartRate} bpm`;
        hr_text = `${hrm.heartRate} bpm`;

        let hr_progress_el = document.getElementById("hr_progress");
        hr_progress_el.text = animateBar(17, hrm.heartRate / 200);
    });
}


// Update the clock every minute
clock.granularity = "seconds";

const myLabel = document.getElementById("time");
const calories_el = document.getElementById("calories");
const steps_el = document.getElementById("steps");

function animateBar(width, percentage) {
    // Define a function that given a percentage, animates test like [||||||     ] based on the percentage. The function
    // should take a parameter of the width of the bar, and the percentage
    let bar = "";
    let fill = Math.floor(width * percentage);
    for (let i = 0; i < width; i++) {
        if (i < fill) {
            bar += "|";
        } else {
            bar += " ";
        }
    }
    return bar;
}

clock.ontick = (evt) => {
    let today_dt = evt.date;
    let hours = today_dt.getHours();
    hours = zeroPad(hours);
    let mins = zeroPad(today_dt.getMinutes());
    myLabel.text = `${hours}:${mins}`;

    // Update the time progress bar
    let today_progress_el = document.getElementById("time_progress");
    today_progress_el.text = animateBar(17, (hours * 60 + today_dt.getMinutes()) / (24 * 60));

    // Update the bike position
    let time_pct = ((hours * 60 + today_dt.getMinutes()) / (24 * 60)).toFixed(2) * screenWidth;
    let bike_id_el = document.getElementById("bike");
    bike_id_el.x = 0 - 50 + time_pct;

    // steps
    let steps = (today.adjusted.steps / 1000).toFixed(0);
    let goal_steps = (goals.steps / 1000).toFixed(0);
    steps_el.text = `${steps}/${goal_steps}`;
    let steps_progress_el = document.getElementById("steps_progress");
    steps_progress_el.text = animateBar(17, today.adjusted.steps / goals.steps);

    // calories
    let calories = (today.adjusted.calories / 1000).toFixed(1);
    let goal_calories = (goals.calories / 1000).toFixed(1);
    calories_el.text = `${calories}/${goal_calories}`;
    let calories_progress_el = document.getElementById("calories_progress");
    calories_progress_el.text = animateBar(17, today.adjusted.calories / goals.calories);
};


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