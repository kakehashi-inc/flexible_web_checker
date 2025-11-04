function checkWords(s: string, words: string[]): boolean {
    for (var word of words) {
        if (s.indexOf(word) >= 0) {
            return true;
        }
    }
    return false;
}

function searchText(list: string[], text: string): boolean {
    for (var s of list) {
        if (s.indexOf(text) >= 0) {
            return true;
        }
    }
    return false;
}

export function EmptyCss(): void {
    console.log('Start EmptyCss');

    const exclude_words: string[] = ['phpdebugbar', 'sf-dump', 'fa-'];

    const selectores: Array<string> = [];
    for (var i: number = 0; i < document.styleSheets.length; i++) {
        const style = document.styleSheets.item(i);
        const rules = style.cssRules || style.rules;
        for (var j: number = 0; j < rules.length; j++) {
            const role = rules.item(j);
            if ('selectorText' in role) {
                // @ts-ignore
                const text: string = role.selectorText;
                if (checkWords(text, exclude_words)) {
                    continue;
                }

                text.split(',').forEach((sp: string) => {
                    sp = sp.trim();
                    const m = sp.substr(0, 1);
                    if (m == '.' || m == '#') {
                        selectores.push(sp);
                    }
                });
            }
        }
    }

    const classes: Array<string> = [];
    document.querySelectorAll('*[class]').forEach(node => {
        if ('classList' in node) {
            node.classList.forEach((css: string) => {
                if (!checkWords(css, exclude_words)) {
                    if (classes.indexOf(css) == -1) {
                        classes.push(css);
                    }
                }
            });
        }
    });

    const empty_classes: Array<string> = [];
    classes.forEach(css => {
        const search: string = '.' + css;
        if (!searchText(selectores, search)) {
            empty_classes.push(css);
        }
    });
    console.log(empty_classes);

    console.log('End EmptyCss');
}
