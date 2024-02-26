window.addEventListener('DOMContentLoaded', function () {
    var all = document.getElementsByTagName('*')

    for (var i = 0; i < all.length; i++) {
        var elem = all[i];
        if (elem.hasAttribute("data-position")) {
            var boundingBox = elem.getAttribute('data-position').split(" ");
            var bottom = randomIntFromInterval(parseInt(boundingBox[1]), parseInt(boundingBox[3]));
            var left = randomIntFromInterval(parseInt(boundingBox[0]), parseInt(boundingBox[2]));

            cs = getComputedStyle(elem);

            bottom = Math.min(bottom, parseInt(boundingBox[3]) - elem.scrollHeight);
            left = Math.min(left, parseInt(boundingBox[2]) - elem.scrollWidth);

            elem.style.position = 'absolute';
            elem.style.left = left + "px";
            elem.style.bottom = bottom + "px";

        }
        if (elem.hasAttribute("id") &&
            (elem.getAttribute("data-type") !== "address" &&
                elem.getAttribute("data-type") !== "item_list")) {

            var x1 = Math.abs(elem.getBoundingClientRect().left)
            var y1 = Math.abs(elem.getBoundingClientRect().bottom)
            var x2 = x1 + elem.getBoundingClientRect().width
            var y2 = y1 + elem.getBoundingClientRect().height

            console.log("position-absolute;" + elem.id + ";" + x1 + ";" + y1 + ";" + x2 + ";" + y2 + ";"
                + elem.innerHTML + ";");
        }
    }

    function randomIntFromInterval(min, max) {
        return Math.floor(Math.random() * (max - min + 1) + min);
    }
});