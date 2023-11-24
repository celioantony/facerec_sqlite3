from settings import connection
from db.database import migrate
from faces.training import training


"""
To increase the training database, it is necessary to create 
directories with the names of the faces in the respective structure.

Structure of folders:

    datatraining /
        celio_soares /
            face01.png
            face02.png
            face03.png
            face04.png
            face05.png
            face06.png
            
    The name of the images can be random, but and extensions is necessary
    a image
"""
migrate(connection)

training()