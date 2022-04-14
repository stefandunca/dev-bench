import QtQml 2.14

QtObject {
    function getColorHashAsJson() {
        return '[{"segmentLength":4,"colorId":1},{"segmentLength":1,"colorId":11},{"segmentLength":3,"colorId":16},{"segmentLength":1,"colorId":8},{"segmentLength":2,"colorId":5},{"segmentLength":4,"colorId":15},{"segmentLength":2,"colorId":27},{"segmentLength":4,"colorId":7},{"segmentLength":1,"colorId":6},{"segmentLength":4,"colorId":25},{"segmentLength":2,"colorId":2}]'
    }

    function getEmojiHashAsJson() {
        return '["🦪", "🙏", "☘️", "👩‍🎤", "💇🏼‍♂️", "👩🏾‍✈️", "💛", "👩🏾‍🏭", "🏄🏾‍♂️", "⏳", "🤦🏽‍♀️", "💂🏽", "👐🏾", "👊🏾"]'
    }

    function getColorId(publicKey) {
        return '4'
    }

    function getCompressedPk(publicKey) {
        return 'zQ3shtLezsYnu39WMUngvyt78m9jFWaMLZFxGjKQqdzZ8C8rG'
    }
}
