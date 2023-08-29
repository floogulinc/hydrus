---
title: Supported Filetypes
---


## Images

| Filetype   | Extension | MIME type      | Thumbnails | Viewable in Hydrus | Notes                                      |
| ---------- | --------- | -------------- | :--------: | :----------------: | ------------------------------------------ |
| jpeg       | `.jpeg`   | `image/jpeg`   |     ✅     |         ✅         |                                            |
| png        | `.png`    | `image/png`    |     ✅     |         ✅         |                                            |
| static gif | `.gif`    | `image/gif`    |     ✅     |         ✅         |                                            |
| webp       | `.webp`   | `image/webp`   |     ✅     |         ✅         | Animated webp files will display as static |
| tiff       | `.tiff`   | `image/tiff`   |     ✅     |         ✅         |                                            |
| qoi        | `.qoi`    | `image/qoi`    |     ✅     |         ✅         | Quite OK Image Format                      |
| icon       | `.ico`    | `image/x-icon` |     ✅     |         ✅         |                                            |
| bmp        | `.bmp`    | `image/bmp`    |     ✅     |         ✅         | Gets converted to png                      |
| heif       | `.heif`   | `image/heif`   |     ✅     |         ✅         |                                            |
| heic       | `.heic`   | `image/heic`   |     ✅     |         ✅         |                                            |
| avif       | `.avif`   | `image/avif`   |     ✅     |         ✅         |                                            |

## Animations

| Filetype      | Extension | MIME type             | Thumbnails | Viewable in Hydrus | Notes |
| ------------- | --------- | --------------------- | :--------: | :----------------: | ----- |
| animated gif  | `.gif`    | `image/gif`           |     ✅     |         ✅         |       |
| apng          | `.apng`   | `image/apng`          |     ✅     |         ✅         |       |
| heif sequence | `.heifs`  | `image/heif-sequence` |     ✅     |         ✅         |       |
| heic sequence | `.heics`  | `image/heic-sequence` |     ✅     |         ✅         |       |
| avif sequence | `.avifs`  | `image/avif-sequence` |     ✅     |         ✅         |       |

## Video

| Filetype  | Extension | MIME type                | Thumbnails | Viewable in Hydrus | Notes |
| --------- | --------- | ------------------------ | :--------: | :----------------: | ----- |
| mp4       | `.mp4`    | `video/mp4`              |     ✅     |         ✅         |       |
| webm      | `.webm`   | `video/webm`             |     ✅     |         ✅         |       |
| matroska  | `.mkv`    | `video/x-matroska`       |     ✅     |         ✅         |       |
| avi       | `.avi`    | `video/x-msvideo`        |     ✅     |         ✅         |       |
| flv       | `.flv`    | `video/x-flv`            |     ✅     |         ❌         |       |
| quicktime | `.mov`    | `video/quicktime`        |     ✅     |         ✅         |       |
| mpeg      | `.mpeg`   | `video/mpeg`             |     ✅     |         ✅         |       |
| ogv       | `.ogv`    | `video/ogg`              |     ✅     |         ✅         |       |
| realvideo | `.rm`     | `video/vnd.rn-realvideo` |     ✅     |         ✅         |       |
| wmv       | `.wmv`    | `video/x-ms-wmv`         |     ✅     |         ✅         |       |

## Audio

| Filetype       | Extension | MIME type                | Viewable in Hydrus | Notes |
| -------------- | --------- | ------------------------ | :----------------: | ----- |
| mp3            | `.mp3`    | `audio/mp3`              |         ✅         |       |
| ogg            | `.ogg`    | `audio/ogg`              |         ✅         |       |
| flac           | `.flac`   | `audio/flac`             |         ✅         |       |
| m4a            | `.m4a`    | `audio/mp4`              |         ✅         |       |
| matroska audio | `.mkv`    | `audio/x-matroska`       |         ✅         |       |
| mp4 audio      | `.mp4`    | `audio/mp4`              |         ✅         |       |
| realaudio      | `.ra`     | `audio/vnd.rn-realaudio` |         ✅         |       |
| tta            | `.tta`    | `audio/x-tta`            |         ✅         |       |
| wave           | `.wav`    | `audio/x-wav`            |         ✅         |       |
| wavpack        | `.wv`     | `audio/wavpack`          |         ✅         |       |
| wma            | `.wma`    | `audio/x-ms-wma`         |         ✅         |       |

## Applications

| Filetype | Extension | MIME type                       | Thumbnails | Viewable in Hydrus | Notes |
| -------- | --------- | ------------------------------- | :--------: | :----------------: | ----- |
| flash    | `.swf`    | `application/x-shockwave-flash` |     ✅     |         ❌         |       |
| pdf      | `.pdf`    | `application/pdf`               |     ❌     |         ❌         |       |

## Image Project Files


| Filetype  | Extension    | MIME type                     | Thumbnails | Viewable in Hydrus | Notes             |
| --------- | ------------ | ----------------------------- | :--------: | :----------------: | ----------------- |
| psd       | `.psd`       | `image/vnd.adobe.photoshop`   |     ✅     |         ✅         | Adobe Photoshop   |
| clip      | `.clip`      | `application/clip`[^1]        |     ✅     |         ❌         | Clip Studio Paint |
| sai2      | `.sai2`      | `application/sai2`[^1]        |     ❌     |         ❌         | PaintTool SAI2    |
| krita     | `.kra`       | `application/x-krita`         |     ✅     |         ❌         |                   |
| svg       | `.svg`       | `image/svg+xml`               |     ✅     |         ❌         |                   |
| xcf       | `.xcf`       | `application/x-xcf`           |     ❌     |         ❌         | GIMP              |
| procreate | `.procreate` | `application/x-procreate`[^1] |     ✅     |         ❌         | Procreate app     |

## Archives
| Filetype | Extension | MIME type                     | Notes |
| -------- | --------- | ----------------------------- | ----- |
| 7z       | `.7z`     | `application/x-7z-compressed` |       |
| gzip     | `.gz`     | `application/gzip`            |       |
| rar      | `.rar`    | `application/vnd.rar`         |       |
| zip      | `.zip`    | `application/zip`             |       |


[^1]: This filetype doesn't have an official or defacto media type, the one listed was made up for Hydrus.