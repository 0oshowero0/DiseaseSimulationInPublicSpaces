export const lerp = (begin, target, degree) => begin * (1 - degree) + target * degree;
export const lerpCoord = (begin, target, degree) => [
    lerp(begin[0], target[0], degree),
    lerp(begin[1], target[1], degree)
];
