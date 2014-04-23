#include <stdio.h>
#include <stdlib.h>
#include <time.h>

int main() {
	int path [100][100];
	int pathno = 0;
	  int temp;
	int Nnode[100], Cnode[100];
	int Nnode_count = 0;
	int Cnode_count = 0;
	int MultiPath[100][100];
	int Group = 0;
	int G_count[100];
	int G_chk[100];
	int set[100];
	//Enter # of paths
	/*printf("How many paths: ");
	  scanf("%d",&pathno);*/

       	//File reader
	FILE *fp,*fp2;
	int temp2;

	fp2 = fopen("pathcaching.txt", "r");
	if (fp2 == NULL) {
		{
			perror("Error while opening the file.\n");
			return 0;
		}
	}

	int ch;
	while(EOF != (ch = fgetc(fp2))) {
	  if(ch == '\n') {
	    pathno++;
	    printf("%d",pathno);
	  }
	}
	
	fclose(fp2);
	
	fp = fopen("pathcaching.txt", "r");
	if (fp == NULL) {
		{
			perror("Error while opening the file.\n");
			return 0;
		}
	}


	int x = 0;
	int y = 0;
	while (!feof(fp)) {
		fscanf(fp,"%d ", &temp2);
		if ( x < pathno ) {
			if (temp2 == -1) {
				x++;
				y=0;
			}
			else {
				path[x][y] = temp2;
				y++;
			}
		}
	}

	fclose(fp);
	//
	//Path info
	/*for(int i=0; i<pathno; i++) {
		printf("How many nodes in path %d: ",i);
		scanf("%d",&temp);	
		for(int j=0; j<temp; j++) {
			printf("Enter name of node %d of the path %d: ",j,i);
			scanf("%d",&path[i][j]);
		}
	}*/

	//Show all inputs
	for(int i=0; i<pathno; i++) {
		int j=0;
		printf("\npath %d: ",i);
		while(path[i][j]>0){
			printf("- %d - ",path[i][j]);
			j++;
		}
	}

	//Show all nodes
	 for(int i=0; i<pathno; i++) {
		int j=0;
		while(path[i][j]>0){
			int cond = 0;
			for(int n=0; n<Cnode_count + 1; n++) {
				if(Cnode[n] == path[i][j]) {
					cond = 1;
				}
			}
			if(cond == 0) {
				Cnode[Cnode_count] = path[i][j];
				Cnode_count++;
			}
			j++;
		}
	}

	//////////////////Start finding necessary and unnecessary nodes//////////////////
	//Find the paths that have the same first and last nodes
	int first,last;
	for(int i=0; i<pathno; i++) {
		set[i] = i;
	}

	for(int i=0; i<pathno; i++) {
		if(set[i] > -1) {
			int j = 0;
			int count = 0;
			G_count[Group] = i;
			G_chk[Group] = 0;
			while(path[i][j]>0) {
				j++;
			}
			first = path[i][0];
			last = path[i][j-1];
			for( int k=0; k<pathno; k++ ) {
				int l=0;
				while(path[k][l]>0) {
					l++;
				}
				if(path[k][0] == first && path[k][l-1] == last) {
					count++;
					//Grouping Paths
					MultiPath[Group][i] = 1;
					MultiPath[Group][k] = 1;
					set[k] = -1;
					if( k>G_count[Group] ) { 
						G_count[Group] = k;
					}
					//count # of paths in the group
					G_chk[Group]++;
				}
			}
			Group++;

			//Find Necessary nodes from unique paths
			if(count == 1) {
				int j=0;
				while(path[i][j]>0) {
					int cond = 0;
					for(int n=0; n<Nnode_count + 1; n++) {
						if(Nnode[n] == path[i][j]) {
							cond = 1;
						}
					}

					//Remove those nodes from Candidate nodes
					if(cond == 0) {
						Nnode[Nnode_count] = path[i][j];
						for(int k=0; k<Cnode_count; k++){
							if(Cnode[k] == Nnode[Nnode_count]){
								Cnode[k] = -1;
							}
						}
						Nnode_count++;
					}
					j++;
				}
			}
		}
	}

	//Find Necessary Nodes from MultiPaths
	for( int l=0; l<Cnode_count; l++) {
		if(Cnode[l] > -1) {
			for(int i=0; i<Group; i++) {
				if (G_chk[i] > 1) {
					int chk = 0;
					for(int j=0; j<G_count[i]+1; j++) {
						if( MultiPath[i][j] > 0 ) {
							int k=0;
							while(path[j][k] > 0) {
								if( path[j][k] == Cnode[l] ) {
									chk++;
								}
							k++;
							}
						}
					}
					if( chk == G_chk[i] ) {
						Nnode[Nnode_count] = Cnode[l];
						Cnode[l] = -1;
						Nnode_count++;
						i = Group;
					}
				}
			}
		}
	}
	//Print groups
	for(int i=0; i<Group; i++) {
		for(int j=0; j<G_count[i]+1; j++) {
			if( MultiPath[i][j] > 0 ) {
				printf("\nGroup %d : Path %d ",i,j);
			}
		}
	}
	//Check if there is at least one Necessary path for each source and destination 
	for(int i=0; i<Group; i++) {
		if (G_chk[i] > 1) {
			int save_chk = 0;
			int save_path;
			//Check paths inside group
			for(int j=0; j<G_count[i]+1; j++) {
				int chk = 0;
				if( MultiPath[i][j] > 0 ) {
					int k=0;
					while(path[j][k] > 0) {
						for( int l=0; l<Nnode_count; l++ ) {
							if ( path[j][k] == Nnode[l] ) {
								chk++;
							}
						}
					k++;
					}
					if( chk > save_chk ) {
							save_chk = chk;
							save_path = j;
						}
					//If there is at least one Necessary path in the group, move to the next group
					if( chk == k ) {
						break;
					}
					//If not, randomly select one path and adjust all nodes to be necessary nodes
					else {
						if( j==G_count[i] ) {
							int k = 0;
							while(path[save_path][k] > 0) {
								for( int l=0; l<Cnode_count; l++ ) {
									if(Cnode[l] > -1) {
										if( path[save_path][k] == Cnode[l] ) {
											Nnode[Nnode_count] = Cnode[l];
											Cnode[l] = -1;
											Nnode_count++;
										}
									}
								}
								k++;
							}
						}	
					}
				}
			}
		}
	}
	
	/////////////////Start Traffic Measurement////////////////////
	//Initialize utilization of all nodes
	int usage_count = 0;
	int usage[100];
	int active_node[100];
	int active_count = 0;
	int inactive_node[100];
	int inactive_count = 0;
	//Print Necessary Nodes
	for(int i=0; i<Nnode_count; i++) {
		printf("\nNecessary Node: %d",Nnode[i]);
		active_node[Nnode[i]] = 1;
		active_count++;
		usage[Nnode[i]] = 0;
		usage_count++;
	}
	//Print Unnecessary Nodes
	for(int i=0; i<Cnode_count; i++) {
		if(Cnode[i]>-1){
			printf("\nUnnecessary Node: %d",Cnode[i]);
			inactive_node[Cnode[i]] = 1;
			inactive_count++;
			usage[Cnode[i]] = 0;
			usage_count++;
		}
	}
	printf("\n");

}
