// @String (label="Directory with MAP2+ images", style="directory") map2Dir
// @String (label="Directory with DAPI images", style="directory") dapiDir
// @String (label="Output directory", style="directory") outputDir

setBatchMode(true);

// Create a results file
resultsPath = outputDir + "/Combined_Results.csv";
File.saveString("Image,Neuron Cell Bodies,Total MAP2+ Area,Average MAP2+ Area per Cell,Neuron Cell Count per Area\n", resultsPath);

processDirectories(map2Dir, dapiDir);

function processDirectories(map2Directory, dapiDirectory) {
    map2List = getFileList(map2Directory);
    dapiList = getFileList(dapiDirectory);

    for (i = 0; i < map2List.length; i++) {
        map2Path = map2Directory + "/" + map2List[i];
        dapiPath = dapiDirectory + "/" + dapiList[i];

        if (endsWith(map2Path, ".tif") && endsWith(dapiPath, ".tif")) {
            processImage(map2Path, dapiPath);
        }
    }
}

function processImage(map2Path, dapiPath) {
    // Process MAP2+ image
    open(map2Path);
    run("Set Scale...", "distance=0 known=0 pixel=1 unit=pixel");
    setAutoThreshold("Otsu");
    run("Convert to Mask");
    run("Measure");
    map2Density = getResult("Mean", nResults-1);
    map2Area = getResult("Area", nResults-1);
    rename("map2Mask");

    // Get image size (area) from the currently opened MAP2+ image
    run("Select All");
    run("Measure");
    imageSize = getResult("Area", nResults-1);
            
    // Process DAPI image
    open(dapiPath);
    run("Set Scale...", "distance=0 known=0 pixel=1 unit=pixel");
    run("Auto Threshold", "method=Otsu");
    run("Open"); // Binary Open
    run("Fill Holes");
    setOption("BlackBackground", false);
    run("Convert to Mask");
    rename("dapiMask");
    
    // Check that both masks are available and perform the colocalization analysis
    if (isOpen("map2Mask") && isOpen("dapiMask")) {
        imageCalculator("AND create", "dapiMask", "map2Mask");
    } else {
        print("Error: One of the required images is not open.");
        return;
    }
        
    // Identify colocalization of neuron bodies with MAP2+
    imageCalculator("AND create", "dapiMask", "map2Mask");
    selectWindow("Result of dapiMask");
    run("Analyze Particles...", "size=235-Infinity circularity=0.00-1.00 display exclude clear include summarize");
    neuronCellCount = nResults;
    
    // Calculate neuron cell count per image area
    neuronCellCountPerArea = neuronCellCount / imageSize;
        
    // Close all images
    close("map2Mask");
    close("dapiMask");
    close("Result of dapiMask");

    // Calculate average MAP2+ area per cell
    if (neuronCellCount > 0) {
        averageMap2AreaPerCell = map2Area / neuronCellCount;
    } else {
        averageMap2AreaPerCell = 0;
    }

    // Append results to the CSV file
    appendResults(resultsPath, File.getName(map2Path), neuronCellCount, map2Area, averageMap2AreaPerCell, neuronCellCountPerArea);
}

function appendResults(filePath, imageName, cellCount, map2Area, avgAreaPerCell, cellcountPerArea) {
    File.append(imageName + "," + cellCount + "," + map2Area + "," + avgAreaPerCell + "," + cellcountPerArea + "\n", filePath);
}

setBatchMode(false);



