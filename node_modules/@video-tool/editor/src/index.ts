import { VideoEditor } from "./editor";
import { TrimOperation } from "./operations/trim";

export { VideoEditor, TrimOperation };
export * from "./editor";
export * from "./operations/trim";

// Create main editor instance with all operations
const editor = new VideoEditor();

// Register operations
editor.registerOperation(new TrimOperation());

export default editor;
