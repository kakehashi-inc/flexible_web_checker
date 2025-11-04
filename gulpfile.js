const { src, dest, task, series, parallel } = require('gulp');
const { execSync } = require('child_process');

const favicons = require("favicons").stream,
    log = require("fancy-log");

const glob = require('glob');
const path = require('path');
const plumber = require('gulp-plumber');
const sass = require('gulp-sass')(require('sass'));
const postcss = require('gulp-postcss');
const cssnano = require('cssnano');
const autoprefixer = require('autoprefixer');
const rename = require('gulp-rename');

var paths = {
    resources: "./frontend",
    static: "./static",
};

function compileParcel(targetBaseDir, file_pattern, outputBaseDir) {
    // baseDir直下のビルド
    log.info('target: ' + targetBaseDir);
    execSync(`npx parcel build ${targetBaseDir}/${file_pattern} --dist-dir ${outputBaseDir} --no-source-maps`);

    // appDir配下のビルド
    const appDir = path.join(targetBaseDir, 'app');
    log.info('target: ' + appDir);
    execSync(`npx parcel build ${appDir}/${file_pattern} --dist-dir ${outputBaseDir} --no-source-maps`);

    // baseDirのapp配下はディレクトリ構造を維持したままtsファイルをparcelでoutputDirにビルド
    // 例：
    // app/test.ts -> outputDir/test.js
    // app/sub/test.ts -> outputDir/sub/test.js

    // appDir配下のディレクトリを取得
    const dirs = glob.sync('*/', { cwd: appDir });

    // 各ディレクトリに対して処理
    dirs.forEach(dir => {
        const dirPath = path.join(appDir, dir);
        const outputSubDir = path.join(outputBaseDir, dir);
        log.info('target: ' + dirPath);
        execSync(`npx parcel build ${dirPath}/${file_pattern} --dist-dir ${outputSubDir} --no-source-maps`);
    });
}

function build_ts(done) {
    compileParcel(path.join(paths.resources, 'ts'), '*.ts*', path.join(paths.static, 'js'));
    done();
}

function build_js(done) {
    compileParcel(path.join(paths.resources, 'js'), '*.js', path.join(paths.static, 'js'));
    done();
}

function compileScss(target) {
    const cssOutputPath = path.join(paths.static, 'css');

    return src(target)
        .pipe(
            plumber({
                errorHandler: function (err) {
                    log.error(err);
                    this.emit('end');
                },
            })
        )
        .pipe(sass({
            errLogToConsole: true,
            includePaths: [path.resolve(__dirname, 'node_modules')]
        }))
        .pipe(postcss([autoprefixer({ cascade: false })]))
        .pipe(dest(cssOutputPath));
}

function minifyCss(target) {
    const cssOutputPath = path.join(paths.static, 'css');

    return src(target)
        .pipe(
            plumber({
                errorHandler: function (err) {
                    log.error(err);
                    this.emit('end');
                },
            })
        )
        .pipe(
            postcss([
                cssnano({
                    preset: [
                        'default',
                        {
                            colormin: false,
                            discardComments: { removeAll: true },
                        },
                    ],
                }),
            ])
        )
        .pipe(rename({ suffix: '.min' }))
        .pipe(dest(cssOutputPath));
}

function build_scss(done) {
    const baseDir = path.join(paths.resources, 'scss');

    const targetFiles = glob.sync('*.scss', { cwd: baseDir });

    const tasks = targetFiles.map(file => {
        const fullPath = path.join(baseDir, file);
        return function processCssTask(cb) {
            log.info(fullPath);
            return series(
                () => compileScss(fullPath),
                () => minifyCss(path.join(paths.static, 'css', file.replace('.scss', '.css')))
            )(cb);
        };
    });

    return series(...tasks)(done);
}

function setup_swal() {
    const packageJsonPath = require.resolve('sweetalert2/package.json');
    const basePath = path.dirname(packageJsonPath);

    return src(path.join(basePath, 'dist/**')).pipe(
        dest(path.join(paths.static, "assets/libs/sweetalert2"))
    );
}

function setup_fa() {
    const packageJsonPath = require.resolve('@fortawesome/fontawesome-free/package.json');
    const basePath = path.dirname(packageJsonPath);

    return src(path.join(basePath, 'webfonts/**')).pipe(
        dest(path.join(paths.static, "assets/fonts/fontawesome"))
    );
}

function make_icons() {
    return src(path.join(paths.resources, "favicons/favicon.png"))
        .pipe(
            favicons({
                appName: "Flexible Web Checker", // Your application's name. `string`
                appShortName: "Web Checker", // Your application's short_name. `string`. Optional. If not set, appName will be used
                appDescription: "Web Checker", // Your application's description. `string`
                developerName: "Kakehashi", // Your (or your developer's) name. `string`
                developerURL: "https://kakehashi-services.com/", // Your (or your developer's) URL. `string`
                lang: "ja-JP",
                background: "#ffffff", // Background colour for flattened icons. `string`
                theme_color: "#456fb6", // Theme color user for example in Android's task switcher. `string`
                appleStatusBarStyle: "black-translucent", // Style for Apple status bar: "black-translucent", "default", "black". `string`
                display: "standalone", // Preferred display mode: "fullscreen", "standalone", "minimal-ui" or "browser". `string`
                orientation: "portrait", // Default orientation: "any", "natural", "portrait" or "landscape". `string`
                path: "favicons/",
                html: "fav_index.html",
                url: "https://kakehashi-services.com/",
                scope: "/", // set of URLs that the browser considers within your app
                start_url: "/?utm_source=homescreen", // Start URL when launching the application from a device. `string`
                version: "1.0.0", // Your application's version string. `string`
                logging: false, // Print logs to console? `boolean`
                pixel_art: false, // Keeps pixels "sharp" when scaling up, for pixel art.  Only supported in offline mode.
                loadManifestWithCredentials: true, // Browsers don't send cookies when fetching a manifest, enable this to fix that. `boolean`
                icons: {
                    android: true, // Create Android homescreen icon. `boolean` or `{ offset, background, mask, overlayGlow, overlayShadow }`
                    appleIcon: true, // Create Apple touch icons. `boolean` or `{ offset, background, mask, overlayGlow, overlayShadow }`
                    appleStartup: false, // Create Apple startup images. `boolean` or `{ offset, background, mask, overlayGlow, overlayShadow }`
                    coast: false, // Create Opera Coast icon. `boolean` or `{ offset, background, mask, overlayGlow, overlayShadow }`
                    favicons: true, // Create regular favicons. `boolean` or `{ offset, background, mask, overlayGlow, overlayShadow }`
                    firefox: false, // Create Firefox OS icons. `boolean` or `{ offset, background, mask, overlayGlow, overlayShadow }`
                    windows: true, // Create Windows 8 tile icons. `boolean` or `{ offset, background, mask, overlayGlow, overlayShadow }`
                    yandex: false, // Create Yandex browser icon. `boolean` or `{ offset, background, mask, overlayGlow, overlayShadow }`
                },
                pipeHTML: true,
                replace: true,
            })
        )
        .on("error", log)
        .pipe(dest(paths.static + "/assets/favicons"));
}

// Run:
// Builds TypeScript
task('build-ts', series(build_ts));

// Run:
// Builds JavaScript
task('build-js', series(build_js));

// Run:
// Compiles & Minifies
task('build-scss', series(build_scss));

// Run:
// Setup libraries
task("setup-libs", parallel(setup_swal));

// Run:
// Setup FontAwesome
task("setup-fa", series(setup_fa));

// Run:
// Make favicons
task("icons", series(make_icons));
