// View Transitions API type augmentation
// Safari 17- doesn't support this; the runtime check handles graceful degradation.

interface ViewTransition {
  finished: Promise<void>
  ready: Promise<void>
  updateCallbackDone: Promise<void>
}

interface Document {
  startViewTransition?(callback: () => Promise<void> | void): ViewTransition
}
