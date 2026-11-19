import assert from "node:assert/strict";
import { test } from "node:test";
import { gapsToNextHigherRank } from "../assets/js/features/ewige-rangliste.js";

test("Gleichstand verwendet den Abstand zur nächsthöheren Ranggruppe", () => {
    const players = [100, 90, 90, 89, 80, 80, 80, 75]
        .map(spiele => ({ spiele }));
    assert.deepEqual(
        gapsToNextHigherRank(players),
        ["–", "10", "10", "1", "9", "9", "9", "5"]
    );
});

test("Gleichstand in der Spitzengruppe bleibt ohne höheren Rang", () => {
    const players = [50, 50, 50, 48, 48, 47]
        .map(spiele => ({ spiele }));
    assert.deepEqual(
        gapsToNextHigherRank(players),
        ["–", "–", "–", "2", "2", "1"]
    );
});

test("Einzige Position hat keinen Abstand", () => {
    assert.deepEqual(gapsToNextHigherRank([{ spiele: 3 }]), ["–"]);
});
