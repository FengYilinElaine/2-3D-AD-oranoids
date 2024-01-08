macro "Batch Colocalization Analysis" {
    // 设置两个文件夹的路径
    folder1Path = "/Users/ellinfff/Desktop/AD类器官&电生理/DATA/images quantification 20231106/sox2map2/ctr/sox2_a"; // 修改为你的文件夹路径
    folder2Path = "/Users/ellinfff/Desktop/AD类器官&电生理/DATA/images quantification 20231106/sox2map2/ctr/map2_a"; // 修改为你的文件夹路径
  
  // 指定结果保存的文件夹路径
    outputFolder = "/Users/ellinfff/Desktop/AD类器官&电生理/DATA/images quantification 20231106/sox2gfap/abeta"; // 修改为你希望保存结果的文件夹路径
    File.makeDirectory(outputFolder); // 创建结果文件夹

    // 获取文件列表
    list1 = getFileList(folder1Path);
    list2 = getFileList(folder2Path);
   
    // 检查两个文件夹中的图像数量是否一致
    if (list1.length != list2.length) {
        print("Error: The number of images in the two folders is not the same.");
    } else {
        // 循环处理图像
        for (i = 0; i < list1.length; i++) {
            image1Path = folder1Path + "/" + list1[i];
            image2Path = folder2Path + "/" + list2[i];

            // 打开图像
            open(image1Path);
            open(image2Path);

            // 执行Colocalization Finder插件
            run("Colocalization Finder", "image1=Image1 image2=Image2 scatterplot_size=[_256 x 256_]");
            call("Colocalization_Finder.setScatterPlotRoi", 0, 255, 0, 255);
           output = call("Colocalization_Finder.analyzeByMacro", "true", "false");

 // 关闭打开的图像
            close("*");
        }

        // 构建结果文件的完整路径
        csvFile = outputFolder + "/colocalization_results.csv";

        // 保存整个output为CSV文件
        File.saveString(output, csvFile);

        print("共定位分析完成，结果已保存为CSV文件: " + csvFile);
    }
}







