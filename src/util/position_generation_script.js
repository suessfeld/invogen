window.addEventListener('load', function () {
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
            (!elem.hasAttribute("data-type") &&
                !elem.getAttribute("data-type") === "address" &&
                !elem.getAttribute("data-type") === "item_list")) {
            console.log("position-absolute;" + elem.id + ";" + left + ";" + bottom + ";"
                + (left + elem.scrollWidth) + ";" + (bottom + elem.scrollHeight) + ";"
                + elem.innerHTML + ";");
        }
    }

    function randomIntFromInterval(min, max) {
        return Math.floor(Math.random() * (max - min + 1) + min);
    }
});