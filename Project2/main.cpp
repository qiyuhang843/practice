#include <opencv2/opencv.hpp>
#include <iostream>

using namespace cv;
using namespace std;

// ˮӡǶ�뺯��
void embedWatermark(const Mat& srcImage, const Mat& watermark, Mat& destImage, float alpha) {
    // ������ԭͼ��С��ͬ�ĸ�����ͼ��
    Mat floatImage;
    srcImage.convertTo(floatImage, CV_32FC3, 1.0 / 255.0);

    // ������ˮӡ��С��ͬ�ĸ�����ˮӡͼ��
    Mat floatWatermark;
    watermark.convertTo(floatWatermark, CV_32FC3, 1.0 / 255.0);

    // ����ˮӡͼ����ƥ��ԭͼ��С
    Mat resizedWatermark;
    resize(floatWatermark, resizedWatermark, floatImage.size());

    // ��ˮӡǶ�뵽ԭͼ��
    for (int i = 0; i < floatImage.rows; i++) {
        for (int j = 0; j < floatImage.cols; j++) {
            for (int k = 0; k < 3; k++) {
                // ��ˮӡǶ�뵽ͼ������ȷ�����
                floatImage.at<Vec3f>(i, j)[k] = (floatImage.at<Vec3f>(i, j)[k] * (1 - alpha)) +
                    (resizedWatermark.at<Vec3f>(i, j)[k] * alpha);
            }
        }
    }

    // ��������ͼ��ת���� 8 λͼ��
    floatImage.convertTo(destImage, CV_8UC3, 255.0);
}

// ˮӡ��ȡ����
void extractWatermark(const Mat& srcImageWithWatermark, const Mat& originalImage, Mat& extractedWatermark, float alpha) {
    // �������ˮӡͼ���С��ͬ�ĸ�����ͼ��
    Mat floatWatermarkedImage;
    srcImageWithWatermark.convertTo(floatWatermarkedImage, CV_32FC3, 1.0 / 255.0);

    // ������ԭʼͼ���С��ͬ�ĸ�����ͼ��
    Mat floatOriginalImage;
    originalImage.convertTo(floatOriginalImage, CV_32FC3, 1.0 / 255.0);

    // ������������ȡˮӡͼ��
    extractedWatermark = Mat::zeros(floatOriginalImage.size(), CV_32FC3);

    // ��ȡǶ���ˮӡ
    for (int i = 0; i < floatOriginalImage.rows; i++) {
        for (int j = 0; j < floatOriginalImage.cols; j++) {
            for (int k = 0; k < 3; k++) {
                // ��ȡǶ����ͼ���е�ˮӡ
                extractedWatermark.at<Vec3f>(i, j)[k] = (floatWatermarkedImage.at<Vec3f>(i, j)[k] - floatOriginalImage.at<Vec3f>(i, j)[k]) / alpha;
            }
        }
    }

    // ����������ȡˮӡͼ��ת���� 8 λͼ��
    extractedWatermark.convertTo(extractedWatermark, CV_8UC3, 255.0);
}

int main() {
    // ��ȡԭʼͼ���ˮӡͼ��
    Mat originalImage = imread("original.jpg");
    Mat watermark = imread("watermark.png");

    if (originalImage.empty() || watermark.empty()) {
        cerr << "Error: Unable to read images." << endl;
        return -1;
    }

    // Ƕ��ˮӡ
    Mat watermarkedImage;
    float alpha = 0.1; // ˮӡǿ��
    embedWatermark(originalImage, watermark, watermarkedImage, alpha);

    // ����Ƕ��ˮӡ���ͼ��
    imwrite("watermarked.jpg", watermarkedImage);

    // ��ȡˮӡ
    Mat extractedWatermark;
    extractWatermark(watermarkedImage, originalImage, extractedWatermark, alpha);

    // ������ȡ��ˮӡͼ��
    imwrite("extracted_watermark.jpg", extractedWatermark);

    // ��ʾ���
    imshow("Original Image", originalImage);
    imshow("Watermark", watermark);
    imshow("Watermarked Image", watermarkedImage);
    imshow("Extracted Watermark", extractedWatermark);
    waitKey(0);

    return 0;
}