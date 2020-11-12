#### Orginal Developer: Jordan Bales
#### Original Date: 9/1/2020
#### The purpose of this application ...

############################ Necessary Libraries ################################
library(shiny)
library(DT)
library(leaflet)
library(shinydashboard)
library(dashboardthemes)
library(shinycssloaders)
#library(reticulate)

#This has to be uncommented to run locally
#use_condaenv("DisasterSat2", required = TRUE)

# ### Define any Python packages needed for the app here:
PYTHON_DEPENDENCIES = c("pip==19.0.3", #Added to fix Warning: Error in : invalid version specification ‘20.3b1’
                        "absl-py==0.11.0",
                        "astor==0.8.1",
                        "cached-property==1.5.2",
                        "gast==0.4.0",
                        "google-pasta==0.2.0",
                        "grpcio==1.33.2",
                        "h5py==2.10.0",
                        "imantics==0.1.12",
                        "joblib==0.17.0",
                        "keras==2.3.0",
                        "keras-applications==1.0.8",
                        "keras-preprocessing==1.1.2",
                        "lxml==4.6.1",
                        "markdown==3.3.3",
                        "numpy==1.19.4",
                        "opencv-python==4.4.0.46",
                        "pandas==1.1.4",
                        "pytz==2020.4",
                        "pyyaml==5.3.1",
                        "scikit-learn==0.23.2",
                        "scipy==1.5.4",
                        "shapely==1.7.1",
                        "simplification==0.5.7",
                        "sklearn==0.0",
                        "tensorboard==1.14.0",
                        "tensorflow==1.14.0",
                        "tensorflow-estimator==1.14.0",
                        "termcolor==1.1.0",
                        "threadpoolctl==2.1.0",
                        "tqdm==4.51.0",
                        "werkzeug==1.0.1",
                        "wrapt==1.12.1",
                        "xmljson==0.2.1"
                        )


############################ User Interface ################################
ui <- shinyUI(
    
    dashboardPage(
        dashboardHeader(title = "Disaster Sat Capstone"), #Open to suggestions
        dashboardSidebar(
            sidebarMenu(
                menuItem("About Us",icon = icon("user-friends"), href = "https://google.com"),
                menuItem("Source code", icon = icon("github"), href = "https://github.com/wcarruthers/xview2_uva"),
                menuItem("Dataset Information",icon = icon("paper-plane"), href = "https://openaccess.thecvf.com/content_CVPRW_2019/papers/cv4gc/Gupta_Creating_xBD_A_Dataset_for_Assessing_Building_Damage_from_Satellite_CVPRW_2019_paper.pdf"),
                menuItem("xView2 Algorithm", icon = icon("github"), href = "https://github.com/DIUx-xView/xView2_baseline"),
                menuItem("Save the Children",icon = icon("hospital"), href = "https://www.savethechildren.org/"),
                
                #Selector for Preloaded or custom
                selectInput(inputId = "customselector",
                            label = "User or Pre-Loaded Images?",
                            choices = c(Custom = "Custom", PreLoaded = "Pre-Loaded")),
                
                conditionalPanel(condition = "input.customselector == 'Custom'",

                #file input for Befor Image
                fileInput(inputId = 'BeforeFile',
                          label ="Please upload your before image",
                          accept = c('.png'),
                          multiple = FALSE),
                
                #file input for After Image
                fileInput(inputId = 'AfterFile',
                          label ="Please upload your before image",
                          accept = c('.png'), 
                          multiple = FALSE),
                
                #Action button to run Python script.
                actionButton("PythonButton", "Analyze")
                
                )#Ends Conditional panel argument
            )),
        
        dashboardBody(
            shinyDashboardThemes(theme = "purple_gradient"),
            
                mainPanel(
                    fluidPage(
                    fluidRow(
                        column(7, 
                        h2("Infrastructure Analysis",align = "center",style="font-family: 'Lobster',
                                 cursive;
                                 font-size: 16;
                                 font-weights: 500;
                                 line-height: 1.1;"),
                        withSpinner(imageOutput('outputImage'))
                        
                        ), 
                        column(3, offset = 2,
                               h2("Before Damage",align = "center",style="font-family: 'Lobster',
                                 cursive;
                                 font-size: 16;
                                 font-weights: 500;
                                 line-height: 1.1;"),
                        imageOutput('outputBeforeImage')
                        )),
                    fluidRow(
                        column(3, offset = 9,
                               h2("After Damage", align = "center",style="font-family: 'Lobster',
                                 cursive;
                                 font-size: 16;
                                 font-weights: 500;
                                 line-height: 1.1;"),
                        imageOutput('outputAfterImage'))
                    )
                        
                        #DT::dataTableOutput("TableResults", width = "100%", height = "100%")
                        
                        ) )
                
            )))
############################ Server Details ################################
server <- shinyServer(function(input,output,session) {
    
######################################### App virtualenv Setup  ################################################           
    
        virtualenv_dir = Sys.getenv('VIRTUALENV_NAME')
        python_path = Sys.getenv('PYTHON_PATH')
        
        # Create virtual env and install dependencies
        reticulate::virtualenv_create(envname = virtualenv_dir, python = python_path)
        reticulate::virtualenv_remove(envname = virtualenv_dir, packages = "pip") #Added to fix Warning: Error in : invalid version specification ‘20.3b1’
        reticulate::virtualenv_install(virtualenv_dir, packages = PYTHON_DEPENDENCIES, ignore_installed=TRUE)
        reticulate::use_virtualenv(virtualenv_dir, required = T)

######################################### Handle Data Inputs ################################################   
    
    ##### Handle storage and use of the Before Satellite png file
    observeEvent(input$BeforeFile, {
        inFile <- input$BeforeFile
        if (is.null(inFile))
            return()
        # file.copy(inFile$datapath, file.path("xview_auto/xview2/test/", inFile$name),overwrite = T) #Need to figure out overwrite
        file.copy(inFile$datapath, file.path("xview_auto/xview2/test/", "Before_Image_File.png"),overwrite = T) #Need to figure out overwrite
    })
    
    ##### Handle storage and use of the After Satellite png file
    observeEvent(input$AfterFile, {
        inFile2 <- input$AfterFile
        if (is.null(inFile2))
            return()
        #file.copy(inFile2$datapath, file.path("xview_auto/xview2/test/", inFile2$name)) #Need to figure out overwrite
        file.copy(inFile2$datapath, file.path("xview_auto/xview2/test/", "After_Image_File.png"),overwrite = T) #Need to figure out overwrite
    })
    
######################################### Python Script execution  ################################################   
    
    #### Action button to run Python Script
    observeEvent(input$PythonButton,{
        req(input$BeforeFile)
        req(input$AfterFile)
        
        #Calls the Xview Python script
        source_python("xview_auto/apply_inference.py")
    })
    
    
######################################### Image Ouput Section ################################################   
    
    #### Image Output 
        #This will display the image created from apply_inference.py
    output$outputImage <- renderImage({
        
        if(input$customselector== "Custom") {
        #Requirements before predict image will be displayed
        req(input$BeforeFile)
        req(input$AfterFile)
        req(input$PythonButton)
        
        # So when the Python script runs it will always produce this file name so it is okay to code this way 
        list(src = 'xview_auto/xview2/test/mexico-earthquake_00000004_prediction.png',
             contentType='.png',
             width = 580,
             height= 580)

        #No clue why this doesn't work but should make it dynamic
        #width = session$clientData$output_outputImage_width,
        #height=session$clientData$output_outputImage_height)

    #}, deleteFile = FALSE) 
    } else {
        list(src = 'xview_auto/xview2/test/PreLoad_prediction.png',
             contentType='.png',
             width = 580,
             height=580)
    }
    
}, deleteFile = FALSE) 
    
    #### Image Output for Before Image
    output$outputBeforeImage = renderImage({
        if(input$customselector== "Custom") {
        #Requirements before Before Image will be displayed
        req(input$BeforeFile)
        
        #BeforeFile=list.files(path = 'xview_auto/xview2/test/',pattern='pre_.*\\.png')
        #outfile2 <- file.path(paste('xview_auto/xview2/test/', BeforeFile,sep = "")) 
        # outfile2 <- file.path("xview_auto/xview2/test/", input$BeforeFile$name)
        outfile2 <- file.path("xview_auto/xview2/test/", "Before_Image_File.png")
        contentType <- '.png'
        
        list(src = outfile2,
             contentType=contentType,
             width = 350,
             height=350)
    #}, deleteFile = FALSE)
        } else {
            list(src = 'xview_auto/xview2/test/PreLoad_Before_Image.png',
                 contentType='.png',
                 width = 350,
                 height=350) 
        }
    }, deleteFile = FALSE)
    
    #### Image Output for After Image
    output$outputAfterImage = renderImage({
        if(input$customselector== "Custom") {
            #Requirements before After Image will be displayed
        req(input$AfterFile)
        
        #BeforeFile=list.files(path = 'xview_auto/xview2/test/',pattern='pre_.*\\.png')
        #outfile2 <- file.path(paste('xview_auto/xview2/test/', BeforeFile,sep = "")) 
        #outfile3 <- file.path("xview_auto/xview2/test/", input$AfterFile$name)
        outfile3 <- file.path("xview_auto/xview2/test/", "After_Image_File.png")
        contentType <- '.png'
        
        list(src = outfile3,
             contentType=contentType,
             width = 350,
             height=350)
    #}, deleteFile = FALSE)
        } else {
            list(src = 'xview_auto/xview2/test/PreLoad_After_Image.png',
                 contentType='.png',
                 width = 350,
                 height= 350) 
        }
    }, deleteFile = FALSE)
    
# Thu Nov  5 12:24:48 2020 ----------------------------- Ask Will's opinion.
    #DataTable output
    #This will display items such as percent of damage, long, lat, etc
    # output$TableResults<- renderDataTable(input$BeforeFile,
    #                                       options = list(
    #                                           pageLength = 5)
    # )
    
    
})

shinyApp(ui = ui, server = server)
