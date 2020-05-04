function updateTextInput(val, id) {
    var bubbleId = id.concat("_value");
    document.getElementById(bubbleId).value = val;
}