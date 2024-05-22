setTimeout(function () {

    var all = document.getElementsByTagName('*')

    for (var i = 0; i < all.length; i++) {
        var elem = all[i];

        if (elem.tagName === "IMG") {
                var img = new Image();
                img.element = elem
                img.onload = function () {
                    this.element.height = this.element.scrollWidth / this.width * this.height
                    calcPositions(this.element)
                }
                img.src = elem.src;
            } else {
                calcPositions(elem)
            }

    }

    function calcPositions(elem) {
        if (elem.hasAttribute("data-position")) {
            var boundingBox = elem.getAttribute('data-position').split(" ");
            var bottom = randomIntFromInterval(parseInt(boundingBox[1]), parseInt(boundingBox[3]));
            var left = randomIntFromInterval(parseInt(boundingBox[0]), parseInt(boundingBox[2]));

            var width = elem.scrollWidth
            var heigth = elem.scrollHeight

            if (elem.tagName === "IMG") {
                console.log(width + " " + heigth)
            }

            bottom = Math.min(bottom, parseInt(boundingBox[3]) - heigth);
            left = Math.min(left, parseInt(boundingBox[2]) - width);

            if (width >= parseInt(boundingBox[2]) - parseInt(boundingBox[0])) {
                left = parseInt(boundingBox[0]) + (parseInt(boundingBox[2]) - parseInt(boundingBox[0])) / 2 - width / 2
            }

            if (heigth >= parseInt(boundingBox[3]) - parseInt(boundingBox[1])) {
                bottom = parseInt(boundingBox[1]) + (parseInt(boundingBox[3]) - parseInt(boundingBox[1])) / 2 - heigth / 2
            }

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
}, 300)