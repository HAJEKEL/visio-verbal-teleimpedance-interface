import Controller from "./components/Controller";
// This imports the Controller component from the specified path

// This is the Parent component called App
function App() {
    return (
        // The div is a block-level element, taking up the full width available, stacking vertically with other block-level elements.
        <div>
            {/* This is the child component called Controller */}
            <Controller />
        </div>
    );
}

export default App;
// This exports the App component as the default export of this module
