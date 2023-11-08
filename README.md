# DuduTracker

A Software to Simulate and Understand Insect Movements over time and space. Dudutracker, 
is designed to simulate and comprehend insect movements over time and space, uses the 
principles of cellular automata. In the insect-related context, the cells can be in three 
potential states: unoccupied, colonized, or exposed. The software uses a 2D grid, with each 
cell having eight neighboring cells. The transition of a cell's state, which represents insect 
dispersal, depends on its current state and the states of its neighbors. A mathematical function 
determines the likelihood of insects colonizing a particular cell based on factors like food 
availability, suitable habitat, or favorable environmental conditions. 

The current code contains the **Django-web** application and the code for the desktop application at:

```iPyDisp.py```

A public version is available at https://dudutracker.monadeware.com

Get help and User guide at: https://dudutracker.monadeware.com/help/


# Deployment of the web application in production mode

In production mode
* Install docker and docker-compose
* Run the following command to create the containers:

    ```docker compose -f ./docker-compose-prod.yml up -d```

* Make migrations:
    * Run the following the get dudu_tracker container id:

    ```docker exec ps```

    * Run the following to apply the migrations
    
    ```docker exec -it <my_container_id> python manage.py migrate```

    * Create a super user with the following command

    ```docker exec -it <my_container_id> python manage.py createsuperuser```

* Now open the application at: 

    ```localhost:8002```  if you are on localhost or : ```your_public_ip_address:8002```


* For building desktop executable we recommend the use of auto-py-to-exe see: <a href="https://github.com/brentvollebregt/auto-py-to-exe">here</a>

* You can also get the desktop app in : ```output/iPyDisp.exe```



* Have fun !!!