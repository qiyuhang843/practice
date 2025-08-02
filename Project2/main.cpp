#include <opencv2/opencv.hpp>
#include <iostream>

using namespace cv;
using namespace std;

// 水印嵌入函数
void embedWatermark(const Mat& srcImage, const Mat& watermark, Mat& destImage, float alpha) {
    // 创建与原图大小相同的浮点型图像
    Mat floatImage;
    srcImage.convertTo(floatImage, CV_32FC3, 1.0 / 255.0);

    // 创建与水印大小相同的浮点型水印图像
    Mat floatWatermark;
    watermark.convertTo(floatWatermark, CV_32FC3, 1.0 / 255.0);

    // 缩放水印图像以匹配原图大小
    Mat resizedWatermark;
    resize(floatWatermark, resizedWatermark, floatImage.size());

    // 将水印嵌入到原图中
    for (int i = 0; i < floatImage.rows; i++) {
        for (int j = 0; j < floatImage.cols; j++) {
            for (int k = 0; k < 3; k++) {
                // 将水印嵌入到图像的亮度分量中
                floatImage.at<Vec3f>(i, j)[k] = (floatImage.at<Vec3f>(i, j)[k] * (1 - alpha)) +
                    (resizedWatermark.at<Vec3f>(i, j)[k] * alpha);
            }
        }
    }

    // 将浮点型图像转换回 8 位图像
    floatImage.convertTo(destImage, CV_8UC3, 255.0);
}

// 水印提取函数
void extractWatermark(const Mat& srcImageWithWatermark, const Mat& originalImage, Mat& extractedWatermark, float alpha) {
    // 创建与带水印图像大小相同的浮点型图像
    Mat floatWatermarkedImage;
    srcImageWithWatermark.convertTo(floatWatermarkedImage, CV_32FC3, 1.0 / 255.0);

    // 创建与原始图像大小相同的浮点型图像
    Mat floatOriginalImage;
    originalImage.convertTo(floatOriginalImage, CV_32FC3, 1.0 / 255.0);

    // 创建浮点型提取水印图像
    extractedWatermark = Mat::zeros(floatOriginalImage.size(), CV_32FC3);

    // 提取嵌入的水印
    for (int i = 0; i < floatOriginalImage.rows; i++) {
        for (int j = 0; j < floatOriginalImage.cols; j++) {
            for (int k = 0; k < 3; k++) {
                // 提取嵌入在图像中的水印
                extractedWatermark.at<Vec3f>(i, j)[k] = (floatWatermarkedImage.at<Vec3f>(i, j)[k] - floatOriginalImage.at<Vec3f>(i, j)[k]) / alpha;
            }
        }
    }

    // 将浮点型提取水印图像转换回 8 位图像
    extractedWatermark.convertTo(extractedWatermark, CV_8UC3, 255.0);
}

int main() {
    // 读取原始图像和水印图像
    Mat originalImage = imread("original.jpg");
    Mat watermark = imread("watermark.png");

    if (originalImage.empty() || watermark.empty()) {
        cerr << "Error: Unable to read images." << endl;
        return -1;
    }

    // 嵌入水印
    Mat watermarkedImage;
    float alpha = 0.1; // 水印强度
    embedWatermark(originalImage, watermark, watermarkedImage, alpha);

    // 保存嵌入水印后的图像
    imwrite("watermarked.jpg", watermarkedImage);

    // 提取水印
    Mat extractedWatermark;
    extractWatermark(watermarkedImage, originalImage, extractedWatermark, alpha);

    // 保存提取的水印图像
    imwrite("extracted_watermark.jpg", extractedWatermark);

    // 显示结果
    imshow("Original Image", originalImage);
    imshow("Watermark", watermark);
    imshow("Watermarked Image", watermarkedImage);
    imshow("Extracted Watermark", extractedWatermark);
    waitKey(0);

    return 0;
}