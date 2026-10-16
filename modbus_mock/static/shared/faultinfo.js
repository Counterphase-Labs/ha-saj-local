export function faultEquipment(description) {
  const faults = description.faults;
  return Object.keys(faults).filter(
    (key) => Array.isArray(faults[key]) && faults[key].length > 0 && typeof faults[key][0] === "object",
  );
}

export function activeFaults(description, state) {
  const items = [];
  const cards = description.faults.cards;
  for (const equipment of faultEquipment(description)) {
    const active = state.faults[equipment] || {};
    for (const bit of description.faults[equipment]) {
      if (active[bit.key]) items.push({ equipment, card: cards[equipment], name: bit.name });
    }
  }
  for (const [pack, codes] of Object.entries(state.faults.packs || {})) {
    if (codes.fault) items.push({ equipment: "packs", card: cards.packs, name: "Pack " + pack + " fault code " + codes.fault });
    if (codes.warning) items.push({ equipment: "packs", card: cards.packs, name: "Pack " + pack + " warning code " + codes.warning });
  }
  return items;
}
