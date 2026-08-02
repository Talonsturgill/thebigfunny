import React from 'react';
import {renderToStaticMarkup} from 'react-dom/server';
import {Character} from '/home/user/thebigfunny/video-engine/src/lib/Character';
const svg = renderToStaticMarkup(React.createElement('svg', {viewBox:'0 0 300 520', xmlns:'http://www.w3.org/2000/svg'},
  React.createElement(Character as any, {frame: 30, outfit: 'flannel', pose: 'stand', build: 'athletic'})));
console.log(svg);
