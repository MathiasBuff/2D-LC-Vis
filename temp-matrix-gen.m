
% get data 
data = get(handles.Open,'userdata');
input_time = data{1}; 
input_value = data{2}; 

% get start and end time in minutes
% use them to calculate time range in seconds, then frequency in Hz
time_end = input_time(end, 1); 
time_start = input_time(1, 1); 

time_span = (input_time(end, 1) - input_time(1, 1)) * 60;
frequency = (size(input_time, 1) - 1) / time_span; 
frequency = round(frequency, 6); 


sampling_time = str2double(get(handles.sw,'String'));


% UI communication values{
 set(handles.ld,'String',time_end) %envoie la valeur dans l'interface (case vérouillée)
 set(handles.fa,'String',frequency)%envoie la valeur dans l'interface (case vérouillée)
 set(handles.stt,'String',time_start)%envoie la valeur dans l'interface (case vérouillée)
 
 xmin =str2double(get(handles.xmin,'String')); % récupération du xmin
 xmax =str2double(get(handles.xmax,'String')); % récupération du xmax
 ymin =str2double(get(handles.ymin,'String')); % récupération du ymin
 ymax =str2double(get(handles.ymax,'String')); % récupération du ymax
 zmin =str2double(get(handles.zmin,'String')); % récupération du zmin
 zmax =str2double(get(handles.zmax,'String')); % récupération du zmax
 g = str2double(get(handles.expZ,'String')); %récupère la valeur donnée pour l'echelle des couleur (exposant sous courbe) 
 
 startcut =str2double(get(handles.startcut,'String')); % récupération du temps de départ des cut
 valvedelay =str2double(get(handles.valvedelay,'String')); % récupération de la valeur du décalage de départ de la vanne
 Colblank =str2double(get(handles.cs,'String')); %numero de la colonne a soustraire (blanc)
 Shifttime=str2double(get(handles.st,'String')); %valeur du delai appliqué aux fractions paires ou impaires
 
 Version=get(handles.Version,'string'); %numero de version pour intégration dans les figures.
%}


% Valve delay chromatogram selection{
 idv=(find(input_time(:,1)>= (time_start+valvedelay/60),1,'first')); % détermine le point de départ des cut (si fractionnement commencé à 5min par ex.)
 input_time = input_time(idv:end); %détermine le vecteur complet a découper sur les valeurs des temps
 input_value = input_value(idv:end); %détermine le vecteur complet a découper sur les valeurs des intensités

 ids=(find(input_time(:,1)>= ((valvedelay/60)+startcut),1,'first')); % trouve le point de départ de la première fraction (temps delay de la vanne inclu)
 input_time = input_time(ids:end);%détermine le vecteur complet a découper sur les valeurs des temps
 input_value = input_value(ids:end);%détermine le vecteur complet a découper sur les valeurs des intensités
%}

% use sampling time to determine number of points per injection in D2
rows_per_column = frequency * sampling_time * 60;
rows_per_column = round(s);

% create the time "column" for D2, then restrict it to the number
% of points calculated above
start_value = 0
step_size = (1/frequency) * (1/60) % step_size in minutes
end_value = sampling_time + step_size
time_column_D2_unsync = transpose([start_value:step_size:end_value]);

time_column_D2 = time_column_D2_unsync (1:rows_per_column);
time_column_D2 = time_column_D2 * 60; % switch the units to seconds



value_matrix = input_value(1:rows_per_column);

H = floor(time_end / sampling_time) * sampling_time; % arrondi de D1 à un multiple du sampling time. permet d'éviter la fraction incomplète en fin de chromato

n = [0 startcut:sampling_time:H-1]; %vecteur final de première dimension (insertion d'un 0 pour la case A1 non prise en compte)
n1 = n(1,(2:end)); %vecteur fraction D1 sans le 0 de remplissage
n2 = n1 + time_start; % ajustement des valeurs de chaque fraction en fonction du temps de départ. (pour un Sampling time de 1 qui commence à 0.1min, donne des fractions à 1.1-2.1-3.1-4.1-5.1 etc..)
%n = n(1:size(value_matrix,2)+1);
for i2 = n2(1, 2:end-1)
    idt = find(input_time(:,1) > i2, 1, 'first') - 1; % trouve la case de départ de chaque fraction
    Z3 = input_value(idt:idt+rows_per_column-1, 1); % crée le vecteur de chaque fraction
    value_matrix = cat (2, value_matrix, Z3); % compile la matrice des fractions précédente et la nouvelle fraction créée
end


A = horzcat(time_column_D2, value_matrix); % combine le temps de 2D avec les cut

B = vertcat(n(1:end-1), A); % combine la matrice 2D avec le vecteur des fraction de première dimension


[M, N] = size(B);%Mlignes, Ncolonnes
%génération des matrices X et Y représentant en Y(temps D1) les data de la ligne 2 à N de la ligne 1, idem pour X(D2) pour data de la colonne 2 à M
[Y, X] = meshgrid(B(1, 2:N), B(2:M, 1)); 

Z = B(2:end, 2:end);



% Blank substraction{
 if Colblank > 0 % si col=0 ou NA, alors pas de soustraction
    Z = Z - repmat(Z(:,Colblank), 1, N-1); %repmat génère une matrice par répétition de la colonne (:,col), sur N-1 col, on soustrait donc a la matrice Z une matrice de même taille correspondant à la colonne choisie
 end 
%}

% Even/Odd Shift Time{
 idt = find(X(:,1) >= Shifttime, 1, 'first');
 
 if get(handles.Cdeven,'Value') == get(handles.Cdeven,'Max')
     Colshift = 1;
 else
     Colshift = 2;
 end
 
 if Shifttime > 0
     for nc = Colshift:2:size(Z,2); %référence de toutes les colonnes paires du Z
         B = Z(:,nc); % création d'une matrice B contenant toutes les colonnes à shift.
         
         %création nouvelle matrice corrigée
         B1 = [B(idt:end,:);
         zeros(idt-1,size(B,2))]; % première partie de la matrice= colonne modifié, zeros... = ajout des lignes manquantes.
 
         % intégration dans Z existant
         Z(:,nc) = B1;
     end
 end 
%}
