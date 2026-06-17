# Initialiser l'heure du compteur de badge

Le compteur de badge dispose d'une horloge sauvegardée par pile. Il n'est donc pas nécessaire de réinitaliser l'heure à chaque fois qu'on le branche.  
Toutefois lorsque l'on doit changer la pile, l'heure n'est pas maintenue et il faut la réinitialiser à l'heure courante.  
L'appareil n'étant pas branché à internet, il ne peut pas déteminer l'heure sur le réseau. Une procédure manuelle est nécessaire.  

Cette procédure implique de modifier un script python pour saisir l'heure à laquelle on veut initialiser l'appareil, puis d'executer ce script.

## Procédure vscode

1. Condition initiale : l'outil VSCode est installé sur un ordinateur, ainsi que le plugin Micropico
2. Branchez le lecteur de badge en USB
3. Ouvrir VSCode
4. Créer ou ouvrir un répertoire micropico: ceci est nécessaire pour avoir accès au filesystème du Pico
    1. Dans vscode menu File / Open folder...
    2. Creez un nouveau répertoire quelconque et sélectionnez le pour ouverture
    3. Initialisez le en tant que répertoire micopico : 
        1. Ouvrez la palette des commandes (Ctrl + shift + p)
        2. Micropico: initialize micropico project
5. Accédez au file systeme du pico : dans la barre d'état en bas de vscode, cliquez sur "Toggle Mpy FS"
6. Un répertoire supplémentaire apparait dans le workspace : Mpy Remote Workspace
7. Cliquez sur le fichier "initialize_time.py" pour l'ouvrir
8. Modifiez la variable `initial_time_tuple` pour mettre l'heure cible
9. Enregistrez le fichier
10. Executez-le : le fichier sélectionné, cliquez sur "Run" dans la barre d'état
11. Le pico est maintenant à l'heure de la variable. Si la pile est chargé, cette heure est maintenue à jour avec le temps qui passe, sinon ce sera l'heure utilisée à chaque redémarrage.
