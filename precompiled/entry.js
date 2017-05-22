var $ = require("jquery");
require("bootstrap");
var React = require("react");
var ReactDOM = require("react-dom");

$(document).ready(function() {
    ReactDOM.render(
        <p>Hello</p>,
        document.getElementById("app-container")
    );
});
