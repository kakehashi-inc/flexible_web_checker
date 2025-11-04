/**
 * 重複送信を防止する
 * @param event 送信イベント
 * @param timeout タイムアウト時間（0以下で無制限）
 * @returns 重複送信を防止した場合はtrue、しなかった場合はfalse
 */
export function preventDuplicateSubmit(event: SubmitEvent, timeout: number) {
    if (!(event instanceof SubmitEvent)) {
        console.error('event is not a SubmitEvent');
        return false;
    } else if (!(event.target instanceof HTMLFormElement)) {
        console.error('event.target is not a HTMLFormElement');
        return false;
    }

    const form = event.target as HTMLFormElement;
    if (form.dataset.submitted) {
        return false;
    }
    form.dataset.submitted = 'true';

    // 送信ボタンを無効化
    let submitButton = null;
    if (
        event.submitter &&
        (event.submitter instanceof HTMLInputElement || event.submitter instanceof HTMLButtonElement)
    ) {
        console.debug(event.submitter);
        submitButton = event.submitter as HTMLInputElement | HTMLButtonElement;
        submitButton.disabled = true; // submitボタンを無効化
    }

    // タイムアウト時間が0以下でない場合はタイムアウト時間を設定
    if (timeout > 0) {
        setTimeout(() => {
            delete form.dataset.submitted;
            submitButton.disabled = false;
        }, timeout);
    }

    return true;
}

/**
 * 重複クリックを防止する
 * @param event クリックイベント
 * @param timeout タイムアウト時間（0以下で無制限）
 * @returns 重複クリックを防止した場合はtrue、しなかった場合はfalse
 */
export function preventDuplicateClick(event: Event, timeout: number) {
    if (!(event.target instanceof HTMLInputElement || event.target instanceof HTMLButtonElement)) {
        console.error('event.target is not a HTMLInputElement or HTMLButtonElement');
        return false;
    }

    const target = event.target as HTMLInputElement | HTMLButtonElement;
    if (target.disabled) {
        return false;
    }
    target.disabled = true;

    // タイムアウト時間が0以下でない場合はタイムアウト時間を設定
    if (timeout > 0) {
        setTimeout(() => {
            target.disabled = false;
        }, timeout);
    }

    return true;
}
