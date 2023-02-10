export class Stateful {
  states = {}

  compare(states) {
    return JSON.stringify(states) === JSON.stringify(this.states)
  }

  set(...args) {
    if (args.length === 2) {
      this.states[args[0]] = args[1]
      return
    }
    this.states = args[0]
  }

  merge(states) {
    this.states = { ...this.states, ...states }
  }

  get(key=null) {
    return key ? this.states[key] : this.states
  }

}
