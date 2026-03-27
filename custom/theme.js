"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.defaultTheme = void 0;
exports.generateTheme = generateTheme;
const tslib_1 = require("tslib");
const tinycolor2_1 = tslib_1.__importDefault(require("tinycolor2"));
function generateColorVariations(defaultColor) {
    const defaultColorObj = (0, tinycolor2_1.default)(defaultColor);
    const darkColor = defaultColorObj.clone().darken(2);
    const baseLight = (0, tinycolor2_1.default)('#ffffff');
    const lightColor = tinycolor2_1.default
        .mix(baseLight, defaultColorObj.toHex(), 12)
        .toHexString();
    const mediumColor = defaultColorObj.clone().lighten(26);
    return {
        default: defaultColorObj.toHexString(),
        dark: darkColor.toHexString(),
        light: lightColor,
        medium: mediumColor.toHexString(),
    };
}
function generateSelectionColor(defaultColor) {
    const defaultColorObj = (0, tinycolor2_1.default)(defaultColor);
    const lightColor = defaultColorObj.lighten(8);
    return lightColor.toHexString();
}
function generateTheme({ primaryColor, fullLogoUrl, favIconUrl, logoIconUrl, websiteName, }) {
    return {
        websiteName,
        colors: {
            avatar: '#515151',
            'blue-link': '#1890ff',
            danger: '#f94949',
            primary: generateColorVariations(primaryColor),
            warn: {
                default: '#f78a3b',
                light: '#fff6e4',
                dark: '#cc8805',
            },
            success: {
                default: '#14ae5c',
                light: '#3cad71',
            },
            selection: generateSelectionColor(primaryColor),
        },
        logos: {
            fullLogoUrl,
            favIconUrl,
            logoIconUrl,
        },
    };
}
exports.defaultTheme = generateTheme({
    primaryColor: '#06B6D4',
    websiteName: 'Turbothal',
    fullLogoUrl: 'https://turbothal.com/brand/turbothal_logo.png?v=2',
    favIconUrl: 'https://turbothal.com/brand/turbothal_logo.png?v=2',
    logoIconUrl: 'https://turbothal.com/brand/turbothal_logo.png?v=2',
});
