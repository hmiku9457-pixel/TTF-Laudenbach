import assert from "node:assert/strict";
import { test } from "node:test";
import { gapsToPreviousPlayer } from "../assets/js/features/ewige-rangliste.js";

test("Gleichstand wird als Gedankenstrich angezeigt", () => {
    const players = [100, 90, 90, 89, 80, 80, 80, 75]
        .map(spiele => ({ spiele }));
    assert.deepEqual(
        gapsToPreviousPlayer(players),
        ["–", "10", "–", "1", "9", "–", "–", "5"]
    );
});

test("Gleichstand in der Spitzengruppe bleibt ohne höheren Rang", () => {
    const players = [50, 50, 50, 48, 48, 47]
        .map(spiele => ({ spiele }));
    assert.deepEqual(
        gapsToPreviousPlayer(players),
        ["–", "–", "–", "2", "–", "1"]
    );
});

test("Einzige Position hat keinen Abstand", () => {
    assert.deepEqual(gapsToPreviousPlayer([{ spiele: 3 }]), ["–"]);
});
