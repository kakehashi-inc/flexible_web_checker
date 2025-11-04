import Request from '@/common/request';

export default class ImageUtils {
    static getDataUrlFromUrl(url: string): Promise<string> {
        return new Promise((resolve, reject) => {
            Request.getCORS(url, null, 180000, { responseType: 'arraybuffer' })
                .then(res => {
                    // 形式をDataURLへ変更
                    const dataUrl =
                        'data:' +
                        res.headers['content-type'] +
                        ';base64,' +
                        Buffer.from(res.data, 'binary').toString('base64');

                    resolve(dataUrl);
                })
                .catch(err => {
                    reject(err);
                });
        });
    }

    static getDataUrlFromBinary(file: Blob | File): Promise<string> {
        return new Promise((resolve, reject) => {
            const reader = new FileReader();
            reader.onload = () => resolve(<string>reader.result);
            reader.onerror = reject;
            reader.readAsDataURL(file);
        });
    }

    static getImageSizeFromDataURL(dataURL: string): Promise<any> {
        return new Promise((resolve, reject) => {
            const img = new Image();
            img.onload = function () {
                const width = img.width;
                const height = img.height;
                resolve({ width, height });
            };
            img.onerror = reject;
            img.src = dataURL;
        });
    }
}
