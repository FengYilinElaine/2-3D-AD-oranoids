inputFolder = getDirectory("/Users/ellinfff/Desktop/AD类器官&电生理/DATA/images quantification 20231106/sox2map2/ctr/sox2");
outputFolder = getDirectory("/Users/ellinfff/Desktop/AD类器官&电生理/DATA/images quantification 20231106/sox2map2/ctr/sox2_a");

// 获取文件列表
list = getFileList(inputFolder);
for (i = 0; i < list.length; i++) {
    // 检查文件是否是图像文件
    if (endsWith(list[i], ".tif") || endsWith(list[i], ".jpg") || endsWith(list[i], ".png") || endsWith(list[i], ".gif")) {
        // 打开图像
        open(inputFolder + list[i]);
        
        // 应用Auto Threshold方法 6e10,iba1 use MaxEntropy; map2,gfap use Li; sox2 use Minimum
        run("Auto Threshold", "method=Minimum");
        
        // 创建新的Auto Threshold后的图像
        title = getTitle();
        run("Convert to Mask");
        
        // 保存处理后的图像
        saveAs("Tiff", outputFolder + title);
        
        // 关闭当前图像
        close();
    }
}

