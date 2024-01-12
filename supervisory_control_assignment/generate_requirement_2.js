/* Run this script to produce on console automaton for requirement 2A or 2B (look at the isForBlue flag) */

const assert = require("assert");

function f(coordinate) {
    switch (coordinate) {
        case 1:
            return "ONE";
        case 2:
            return "TWO";
        case 3:
            return "THREE";
        case 4:
            return "FOUR";
        case 5:
            return "FIVE"
        default:
            assert(false); //this shouldn't happen
            return null;
    }
}

function getNextState(event, currentState, subsetIdentifier) {
    const isEventUncontrollable = event.startsWith("unc");
    const isChargeEvent = event.startsWith("charge");
    if (isEventUncontrollable) {
        event = event.substring(4);
        //check if uncontrollable events are happening at (2,2) or not
        if (currentState.x != 2 || currentState.y != 2) {
            return null;
        }
    }
    //check if charge events are happening at (1,1) or (4,2)
    if (isChargeEvent) {
        if ((currentState.x != 1 || currentState.y != 1) && (currentState.x != 4 || currentState.y != 2)) {
            return null;
        }
    }
    let newState = JSON.parse(JSON.stringify(currentState)); //cloning
    let offsetX, offsetY;
    switch (event) {
        case "left":
            offsetX = -1;
            offsetY = 0;
            break;
        case "right":
            offsetX = 1;
            offsetY = 0;
            break;
        case "up":
            offsetX = 0;
            offsetY = -1;
            break;
        case "down":
            offsetX = 0;
            offsetY = 1;
            break;
        case "charge":
            offsetX = 0;
            offsetY = 0;
            break;
        default:
            assert(false);  //this shouldn't happen
    }
    newState.x += offsetX;
    newState.y += offsetY;
    //check if rover is out of bounds
    if (newState.x < 1 || newState.x > 5 || newState.y < 1 || newState.y > 3) {
        return null;
    }
    //check requirement constraints
    if (subsetIdentifier == "__CHARGED_A" && newState.x == 1 && newState.y == 1 && isChargeEvent) {
        return null;
    } else if (subsetIdentifier == "__CHARGED_B" && newState.x == 4 && newState.y == 2 && isChargeEvent) {
        return null;
    }
    //track charge events
    if (isChargeEvent) {
        if (newState.x == 1 && newState.y == 1) {
            subsetIdentifier = "__CHARGED_A";
        } else if (newState.x == 4 && newState.y == 2) {
            subsetIdentifier = "__CHARGED_B";
        }
    }
    return `${f(newState.x)}_${f(newState.y)}${subsetIdentifier}`;
}

const events = [
    "left",
    "right",
    "up",
    "down",
    "unc_left",
    "unc_right",
    "unc_up",
    "unc_down",
    "charge",
];

const subsetIdentifiers = ["", "__CHARGED_A", "__CHARGED_B"];

const isForBlue = false; //modify this to get requirement for the desired rover

console.log("import \"../plant/events.cif\";");
console.log("requirement Requirement2: /* choose either 2A or 2B*/");

for (let i = 0; i <= 2; i++) {
    let subsetIdentifier = subsetIdentifiers[i];
    for (let x = 1; x <= 5; x++) {
        for (let y = 1; y <= 3; y++) {
            let optionalInitialStatement = i == 0 && (isForBlue && x == 4 && y == 2 || !isForBlue && x == 1 && y == 1) ? "initial;" : ""
            console.log(`\tlocation ${f(x)}_${f(y)}${subsetIdentifier}: ${optionalInitialStatement} marked;`);
            for (const event of events) {
                let nextState = getNextState(event, /* currentState: */ { x: x, y: y }, subsetIdentifier);
                if (nextState != null) {
                    console.log(`\t\tedge ${event}${isForBlue ? "_blue" : "_yellow"} goto ${nextState};`)
                }
            }
        }
    }
}
console.log("end");