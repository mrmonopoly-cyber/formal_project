/* Run this script to produce on console automaton for requirement 3 */

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

function isStateUnsafe(state) {
	//check if a collision can happen due to uncontrollable events
	const uncontrolledMovements = [
		{ x: 2, y: 1 },
		{ x: 1, y: 2 },
		{ x: 2, y: 3 },
		{ x: 3, y: 2 },
	];
	//check if yellow is in an uncontrollable position and blue is "near"
	if (state.xY == 2 && state.yY == 2) {
		if (uncontrolledMovements.some(_ => _.x == state.xB && _.y == state.yB)) {
			return true;
		}
	}
	//check if blue is in an uncontrollable position and yellow is "near"
	if (state.xB == 2 && state.yB == 2) {
		if (uncontrolledMovements.some(_ => _.x == state.xY && _.y == state.yY)) {
			return true;
		}
	}
	return false;
}

function getNextState(event, currentState) {
	const isEventForBlue = event.endsWith("blue");
	const isEventUncontrollable = event.startsWith("unc");
	const isChargeEvent = event.startsWith("charge");
	if (isEventUncontrollable) {
		event = event.substring(4);
		//check if uncontrollable events are happening at (2,2) or not
		if (isEventForBlue && (currentState.xB != 2 || currentState.yB != 2)) {
			return null;
		} else if (!isEventForBlue && (currentState.xY != 2 || currentState.yY != 2)) {
			return null;
		}
	}
	//check if charge events are happening at (1,1) or (4,2)
	if (isEventForBlue && isChargeEvent) {
		if ((currentState.xB != 1 || currentState.yB != 1) && (currentState.xB != 4 || currentState.yB != 2)) {
			return null;
		}
	}
	if (!isEventForBlue && isChargeEvent) {
		if ((currentState.xY != 1 || currentState.yY != 1) && (currentState.xY != 4 || currentState.yY != 2)) {
			return null;
		}
	}
	const movement = event.substring(0, event.indexOf("_" + (isEventForBlue ? "blue" : "yellow")));
	let newState = JSON.parse(JSON.stringify(currentState)); //cloning
	let offsetX, offsetY;
	switch (movement) {
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
	if (isEventForBlue) {
		newState.xB += offsetX;
		newState.yB += offsetY;
	} else {
		newState.xY += offsetX;
		newState.yY += offsetY;
	}
	//check if rovers are out of bounds
	if (newState.xY < 1 || newState.xY > 5 || newState.yY < 1 || newState.yY > 3) {
		return null;
	} else if (newState.xB < 1 || newState.xB > 5 || newState.yB < 1 || newState.yB > 3) {
		return null;
	}
	//check if a collision happened
	if (newState.xY == newState.xB && newState.yY == newState.yB) {
		return null;
	}
	//check if a collision could happen due to uncontrollable movements
	if (isStateUnsafe(newState)) {
		return null;
	}
	return `${f(newState.xY)}_${f(newState.yY)}__${f(newState.xB)}_${f(newState.yB)}`;
}

const events = [
	"left_yellow",
	"right_yellow",
	"up_yellow",
	"down_yellow",
	"unc_left_yellow",
	"unc_right_yellow",
	"unc_up_yellow",
	"unc_down_yellow",
	"charge_yellow",

	"left_blue",
	"right_blue",
	"up_blue",
	"down_blue",
	"unc_left_blue",
	"unc_right_blue",
	"unc_up_blue",
	"unc_down_blue",
	"charge_blue",
];

console.log("import \"../plant/events.cif\";");
console.log("requirement Requirement3:");

for (let xY = 1; xY <= 5; xY++) {
	for (let yY = 1; yY <= 3; yY++) {
		for (let xB = 1; xB <= 5; xB++) {
			for (let yB = 1; yB <= 3; yB++) {
				if (xY == xB && yY == yB || isStateUnsafe(/* currentState: */ { xY: xY, yY: yY, xB: xB, yB: yB })) {
					continue; //don't allow explicit collisions
				}
				let optionalInitialStatement = xY == 1 && yY == 1 && xB == 4 && yB == 2 ? "initial;" : "";
				console.log(`\tlocation ${f(xY)}_${f(yY)}__${f(xB)}_${f(yB)}: ${optionalInitialStatement} marked;`);
				for (const event of events) {
					let nextState = getNextState(event, /* currentState: */ { xY: xY, yY: yY, xB: xB, yB: yB });
					if (nextState != null) {
						console.log(`\t\tedge ${event} goto ${nextState};`)
					}
				}
			}
		}
	}
}

console.log("end");

