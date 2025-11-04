import axios, { AxiosInstance, AxiosResponse, AxiosError } from 'axios';
import Swal, { SweetAlertResult } from 'sweetalert2/dist/sweetalert2.js';
import imageCompression from 'browser-image-compression';

export default class Request {
    static csrf_token = null;

    static getParam(id: string): Promise<FormData> {
        return new Promise(async (resolve, reject) => {
            const form = <HTMLFormElement>document.getElementById(id);
            const form_data = new FormData(form);

            // 画像のベースパスを取得
            var s3_base_url = null;
            const elCF = <HTMLMetaElement>document.head.querySelector('meta[name="cf"]');
            if (elCF) {
                s3_base_url = elCF.content;
            }

            // 画像アップロード関係の追加
            const elList: NodeListOf<HTMLImageElement> = form.querySelectorAll('img.form-data');
            const elArray = Array.from(elList);

            for (var elImg of elArray) {
                if (!elImg.id) {
                    continue;
                }

                if (elImg.src && elImg.src.startsWith('data:image/')) {
                    const file = await imageCompression.getFilefromDataUrl(elImg.src, elImg.id);
                    form_data.append(elImg.id, file);
                } else {
                    // 今回画像を変更していない場合は 〜_src の名前で設定されているアドレスを送信
                    var url_data;
                    if (!elImg.src) {
                        url_data = '';
                    } else if (elImg.src.startsWith('https://dummyimage.com/')) {
                        url_data = '';
                    } else if (elImg.src == location.href) {
                        url_data = '';
                    } else if (s3_base_url && elImg.src.startsWith(s3_base_url)) {
                        url_data = elImg.src.substring(s3_base_url.length);
                    } else {
                        url_data = elImg.src;
                    }

                    // 空文字の場合、対象外になってしまうブラウザがあるため0で送信
                    if (url_data == '') {
                        url_data = '0';
                    }
                    form_data.append(elImg.id + '_src', url_data);
                }
            }

            resolve(form_data);
        });
    }

    static createInstance(timeout: number = 60000): AxiosInstance {
        if (!this.csrf_token) {
            const elMeta = <HTMLMetaElement>document.head.querySelector('meta[name="csrf-token"]');
            if (elMeta) {
                this.csrf_token = elMeta.content;
            }
        }

        var instance;
        if (this.csrf_token) {
            instance = axios.create({
                headers: { 'X-CSRF-TOKEN': this.csrf_token },
                timeout: timeout,
                maxRedirects: 0,
            });
        } else {
            instance = axios.create({
                timeout: timeout,
                maxRedirects: 0,
            });
        }

        instance.interceptors.response.use(
            response => response,
            async (error: AxiosError) => {
                const status = error.response?.status;

                // リダイレクト (300-399)の場合はリダイレクト
                if (status >= 300 && status < 400 && error.response?.headers.location) {
                    window.location.href = error.response.headers.location;
                    return new Promise(() => {});
                }

                // リロードで解消される可能性のあるエラー
                var reload_message = null;
                if (status == 401 || status == 403) {
                    reload_message = '認証関連のエラーが発生しています。ページの再読み込みを行います。';
                } else if (status == 419) {
                    reload_message = 'ページの期限が切れています。ページの再読み込みを行います。';
                }

                // リロードメッセージがある場合は表示してリロード
                if (reload_message) {
                    // ローディング非表示
                    let loading = document.getElementById('loading');
                    if (loading) {
                        // 表示が非同期でONになるのでまるごと削除しておく
                        loading.remove();
                    }

                    // メッセージ表示
                    await Swal.fire({
                        icon: 'warning',
                        text: reload_message,
                    });

                    // OKされたらリロード
                    window.location.reload();
                    return new Promise(() => {});
                }

                // 共通フック対象外の場合はそのままエラーを返す
                return Promise.reject(error);
            }
        );

        return instance;
    }

    static post(
        url: string,
        data: any,
        timeout: number = 180000,
        add_config: any = null
    ): Promise<AxiosResponse<any, any>> {
        const instance = this.createInstance(timeout);
        if (add_config) {
            return instance.post(url, data, add_config);
        } else {
            return instance.post(url, data);
        }
    }

    static async postAs(
        url: string,
        form_id: string,
        timeout: number = 180000,
        add_config: any = null
    ): Promise<AxiosResponse<any, any>> {
        const instance = this.createInstance(timeout);
        const data = await this.getParam(form_id);
        if (add_config) {
            return instance.post(url, data, add_config);
        } else {
            return instance.post(url, data);
        }
    }

    static get(url, params = null, timeout = 60000, add_config = null): Promise<AxiosResponse<any, any>> {
        const instance = this.createInstance(timeout);

        var config = {
            params: params,
        };
        if (add_config) {
            config = { ...config, ...add_config };
        }

        return instance.get(url, config);
    }

    static getCORS(
        url: string,
        params: any = null,
        timeout: number = 180000,
        add_config: any = null
    ): Promise<AxiosResponse<any, any>> {
        // CRSFをつけるとCFでエラーになるので個別で作成
        const instance = axios.create({
            timeout: timeout,
        });

        var config = {
            params: params,
            withCredentials: false,
        };
        if (add_config) {
            config = { ...config, ...add_config };
        }

        return instance.get(url, config);
    }

    static delete(
        url: string,
        params: any = null,
        timeout: number = 60000,
        add_config: any = null
    ): Promise<AxiosResponse<any, any>> {
        const instance = this.createInstance(timeout);

        var config = {
            params: params,
        };
        if (add_config) {
            config = { ...config, ...add_config };
        }

        return instance.delete(url, config);
    }

    static getResponseData(res: any): any {
        var result = null;
        if (res && res.data) {
            result = res.data;
            if (res.data.response) {
                result = res.data.response;
            }
        }
        return result;
    }

    static getErrorData(err: any): any {
        const res = err.response;
        return this.getResponseData(res);
    }

    static clearErrors(form_id: string): void {
        const form = document.getElementById(form_id);

        var rmlist;
        rmlist = form.querySelectorAll('.is-invalid');
        rmlist.forEach(el => {
            el.classList.remove('is-invalid');
        });

        rmlist = form.querySelectorAll('.invalid-feedback');
        rmlist.forEach(el => {
            el.remove();
        });

        const e = form.querySelector('#error_message');
        if (e) {
            e.innerHTML = '';
        }
    }

    static showErrorResponse(err: any, form_id: string, scrollInvalid: boolean = true): void {
        const form = document.getElementById(form_id);

        // 前回エラーの残骸を除去
        this.clearErrors(form_id);

        // エラーデータの処理
        const data = this.getErrorData(err);
        if (data) {
            if (data.errors) {
                for (let key in data.errors) {
                    const error = data.errors[key];
                    if (error[0]) {
                        var target = form.querySelector('#' + key);
                        if (!target) {
                            target = form.querySelector('[name=' + key + ']');
                        }
                        if (target) {
                            const elDiv = document.createElement('div');
                            elDiv.classList.add('invalid-feedback');
                            elDiv.innerHTML = error[0];

                            var parent = <HTMLElement>target.parentNode;
                            var ref_node = target;
                            if (parent) {
                                if (parent.classList.contains('input-group') || target.tagName == 'IMG') {
                                    elDiv.style.display = 'contents';
                                    ref_node = parent;
                                    parent = <HTMLElement>parent.parentNode;
                                } else if (!parent.classList.contains('form-outline')) {
                                    const style = window.getComputedStyle(target);
                                    if (style && style.marginBottom) {
                                        // ターゲットのマージン分引いた位置に表示
                                        const num = parseInt(style.marginBottom.replace('px', ''));
                                        if (!Number.isNaN(num) && num > 0) {
                                            const mt = -Math.round((num * 75) / 100);
                                            const mb = num;
                                            elDiv.setAttribute('style', `margin-top:${mt}px; margin-bottom:${mb}px;`);
                                        }
                                    }
                                }

                                parent.insertBefore(elDiv, ref_node.nextSibling);
                            }

                            target.classList.add('is-invalid');
                        }
                    }
                }
            }

            const e = form.querySelector('#error_message');
            if (e) {
                if (data.message) {
                    e.innerHTML = data.message;
                }
            }
        }

        if (scrollInvalid) {
            // 先頭のエラーにスクロール
            this.scrollFirstInvalid();
        }
    }

    static scrollFirstInvalid(): void {
        // 先頭のエラーにスクロール
        const check = document.querySelector('.is-invalid');
        if (check) {
            check.scrollIntoView({
                behavior: 'auto',
                block: 'center',
            });
        }
    }

    static showErrorMessageDialog(err: AxiosError, process_title: string): Promise<SweetAlertResult<any>> {
        if (err.response && err.response.status && err.response.status >= 400 && err.response.status <= 499) {
            // 400番台のエラーは内容を表示
            const data: any = err.response.data;
            const err_messages = [];

            // ステータス別にエラーの基本情報を設定
            let title;
            let summary;
            switch (err.response.status) {
                case 422:
                    title = '入力チェックエラー';
                    summary = '入力内容に問題があるため、' + process_title + 'に失敗しました。';
                    break;
                case 500:
                    title = process_title + 'エラー';
                    summary = 'サーバーエラーが発生しました。<br/>時間をあけてから再度お試しください。';
                    break;
                case 503:
                    title = process_title + 'エラー';
                    summary = 'サーバーが混雑しています。<br/>しばらくしてから再度お試しください。';
                    break;
                default:
                    title = process_title + 'エラー';
                    if (data && data.message) {
                        summary = data.message;
                    } else {
                        summary = '内容に問題があるため、' + process_title + 'に失敗しました。';
                    }
            }

            // 項目別のエラーメッセージを取得
            if (data && data.errors) {
                Object.keys(data.errors).forEach(function (key) {
                    if (err_messages.length < 5) {
                        err_messages.push(data.errors[key]);

                        if (err_messages.length == 5) {
                            err_messages.push('※ 5件のみ表示しています');
                        }
                    }
                });
            }

            var message = '';
            if (err_messages.length > 0) {
                message = '<br/><br/><small>' + err_messages.join('<br/>') + '</small>';
            }

            return Swal.fire({
                icon: 'warning',
                title: title,
                html: '<div class="text-start">' + summary + message + '</div>',
            });
        } else {
            return Swal.fire({
                icon: 'error',
                title: 'エラー',
                text: process_title + 'に失敗しました。',
            });
        }
    }
}
