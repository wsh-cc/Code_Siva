'use strict'
function add(a, b){
    return a + b;
}

var c, d;
try {
    c = add(1, 2);
    console.log(c);
    d = inc();
    console.log(d);
} catch (ReferceError) {
    console.log(ReferceError);
} finally {
    console.log('*********************************');
}