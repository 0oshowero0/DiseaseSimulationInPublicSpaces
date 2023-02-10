export function genPersonality({
  maleFemaleRate=1.0445,
  infectionRate=0,
                               } = {}) {
  const gender = Math.random() < maleFemaleRate / (1 + maleFemaleRate) ? 0 : 1; // male: 0, female: 1
  const age = Math.round(Math.random() * 70 + 10)
  // const infected = Math.random() < infectionRate // 感染者
  return {
    gender,
    age,
    // infected,
  }
}
