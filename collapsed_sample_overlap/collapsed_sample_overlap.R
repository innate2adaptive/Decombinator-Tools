
# Collapsed samples overlap

# Tahel Ronel, June 2021

# This script calculates the TCR overlap (using the 5-part Decombinator id, DCR) between any two samples produced using Collapsinator from Decombinator V4. 
# The overlap is calculated as follows:
# Let A be the overlap matrix. Then for any two samples i,j, 
# A_{i,j}, the overlap with respect to row i, is
# (Number of distinct DCRs found in both i and j) / (number of unique DCRs in i).

# Note this is in general asymmetric (A_{i,j} is not equal to A_{j,i}).

# The overlap matrix is then plotted as a heatmap, with red squares marking an overlap greater than (mean + 3 standard deviations). 

# If comparing all samples in a particular sequencing run, note that as some runs contain several samples from the same individual/s, 
# the absolute expected 'background' overlap will differ between runs.

# The script calculates and plots the overlap of the alpha files first followed by beta.

library(pheatmap)
library(RColorBrewer)
library(ggplot2)

# Change this to the path to the directory containing the collapsed (.freq) files to be compared
input<-'/path/to/collapsed/files'
dir<-dir(input)

# Alpha

alpha_list<-list()

alpha_idx<-grep('alpha',dir) 
alpha_dir<-dir[alpha_idx]

# Reading in all alpha collapsed files
for (i in 1:length(alpha_dir)){
  alpha_list[[i]]<-read.csv(paste(input,alpha_dir[i],sep=""),header=FALSE) 
}

# Defining the sample names (removing 'dcr' prefix and chain+file suffix to shorten)
s1<-strsplit(alpha_dir, '_alpha.freq.gz')
s2<-strsplit(unlist(s1), 'dcr_')
names_alpha<-lapply(1:length(alpha_dir), function(x){(s2[[x]][2])})

names(alpha_list)<-names_alpha

# Calculating the overlap matrix:
alpha_mat<-matrix(ncol=length(alpha_dir),nrow=length(alpha_dir))

len_alpha<-length(alpha_dir)

for (i in 1:len_alpha){
  for (j in 1:len_alpha){
    dcr_i<-paste(alpha_list[[i]][,1],alpha_list[[i]][,2],alpha_list[[i]][,3],alpha_list[[i]][,4],alpha_list[[i]][,5],sep=" ")
    dcr_j<-paste(alpha_list[[j]][,1],alpha_list[[j]][,2],alpha_list[[j]][,3],alpha_list[[j]][,4],alpha_list[[j]][,5],sep=" ")
    y1<-c(dcr_i,dcr_j)
    total_i<-length(dcr_i)#nrow(alpha_list[[i]])
    total_ij<-length(y1)
    unique_ij<-length(unique(y1))
    C_ij<-total_ij-unique_ij
    alpha_mat[i,j]<-C_ij/total_i
  }}

row.names(alpha_mat)<-names_alpha
colnames(alpha_mat)<-names_alpha

alpha_mat_df<-data.frame(alpha_mat)

# Defining the accepted background threshold as mean + 3 std. devs.:
alpha_1<-which(alpha_mat==1)
alpha_mat_nondiag<-alpha_mat[-alpha_1]
mean_alpha<-mean(alpha_mat_nondiag)
sd_alpha<-sd(alpha_mat_nondiag)

outliers3sd<-mean_alpha+3*sd_alpha
outliers3<-which(alpha_mat_df>=outliers3sd)
outliers3<-setdiff(outliers3,alpha_1)

# Setting parameters for heatmap:
border_colours_alpha<-matrix(ncol=len_alpha, nrow=len_alpha)
border_colours_alpha[-outliers3]<-"grey"
border_colours_alpha[outliers3]<-"red"

bk1 <- c(seq(0,outliers3sd,by=0.005),outliers3sd)
bk2 <- c(outliers3sd+0.0001,seq(outliers3sd+0.0002,0.99,by=0.005))
bk <- c(bk1,bk2)  #combine the break limits for purpose of graphing

my_palette <- c(colorRampPalette(colors = c("lightyellow", "lightblue"))(n = length(bk1)-1),
                "gray38", "gray38",
                c(colorRampPalette(colors = c("red", "darkred"))(n = length(bk2)-1)))


# Plotting the heatmap:
pheatmap(alpha_mat_df,cluster_method="Ward.D",clustering_distance_row ="euclidean" ,main=paste("Sample Overlap, alpha"),treeheight_row=0, cluster_cols = FALSE,cluster_rows = FALSE, col= my_palette, breaks=bk, fontsize = 11,fontsize_row=10,show_rownames = TRUE, border_color = border_colours_alpha)


# Save heatmap image as pdf 
#dev.off()
#pdf(paste("/path/to/folder/overlap_alpha_",Sys.Date(),".pdf",sep=""))
#pheatmap(alpha_mat_df,cluster_method="Ward.D",clustering_distance_row ="euclidean" ,main=paste("Sample Overlap, alpha"),treeheight_row=0, cluster_cols = FALSE,cluster_rows = FALSE, col= my_palette, breaks=bk, fontsize = 11,fontsize_row=10,show_rownames = TRUE, border_color = border_colours_alpha)
#dev.off()



# Beta

beta_list<-list()

beta_idx<-grep('beta',dir) 
beta_dir<-dir[beta_idx]

# Reading in all beta collapsed files
for (i in 1:length(beta_dir)){
  beta_list[[i]]<-read.csv(paste(input,beta_dir[i],sep=""),header=FALSE) 
}

# Defining the sample names (removing 'dcr' prefix and chain+file suffix to shorten)
s1<-strsplit(beta_dir, '_beta.freq.gz')
s2<-strsplit(unlist(s1), 'dcr_')
names_beta<-lapply(1:length(beta_dir), function(x){(s2[[x]][2])})

names(beta_list)<-names_beta

# Calculating the overlap matrix
beta_mat<-matrix(ncol=length(beta_dir),nrow=length(beta_dir))

len_beta<-length(beta_dir)

for (i in 1:len_beta){
  for (j in 1:len_beta){
    dcr_i<-paste(beta_list[[i]][,1],beta_list[[i]][,2],beta_list[[i]][,3],beta_list[[i]][,4],beta_list[[i]][,5],sep=" ")
    dcr_j<-paste(beta_list[[j]][,1],beta_list[[j]][,2],beta_list[[j]][,3],beta_list[[j]][,4],beta_list[[j]][,5],sep=" ")
    y1<-c(dcr_i,dcr_j)
    total_i<-length(dcr_i)#nrow(beta_list[[i]])
    total_ij<-length(y1)
    unique_ij<-length(unique(y1))
    C_ij<-total_ij-unique_ij
    beta_mat[i,j]<-C_ij/total_i
  }}

row.names(beta_mat)<-names_beta
colnames(beta_mat)<-names_beta

beta_mat_df<-data.frame(beta_mat)

# Defining the accepted background threshold as mean + 3 std. devs.:
beta_1<-which(beta_mat==1)
beta_mat_nondiag<-beta_mat[-beta_1]
mean_beta<-mean(beta_mat_nondiag)
sd_beta<-sd(beta_mat_nondiag)

outliers3sd<-mean_beta+3*sd_beta
outliers3<-which(beta_mat_df>=outliers3sd)
outliers3<-setdiff(outliers3,beta_1)

# Setting parameters for heatmap:
border_colours_beta<-matrix(ncol=len_beta, nrow=len_beta)
border_colours_beta[-outliers3]<-"grey"
border_colours_beta[outliers3]<-"red"

bk1 <- c(seq(0,outliers3sd,by=0.005),outliers3sd)
bk2 <- c(outliers3sd+0.0001,seq(outliers3sd+0.0002,0.99,by=0.005))
bk <- c(bk1,bk2)  #combine the break limits for purpose of graphing

my_palette <- c(colorRampPalette(colors = c("lightyellow", "lightblue"))(n = length(bk1)-1),
                "gray38", "gray38",
                c(colorRampPalette(colors = c("red", "darkred"))(n = length(bk2)-1)))

# Plotting the heatmap:
pheatmap(beta_mat_df,cluster_method="Ward.D",clustering_distance_row ="euclidean" ,main=paste("Sample Overlap, beta"),treeheight_row=0, cluster_cols = FALSE,cluster_rows = FALSE, col= my_palette, breaks=bk, fontsize = 11,fontsize_row=10,show_rownames = TRUE, border_color = border_colours_beta)


# Save heatmap image as pdf 
#dev.off()
#pdf(paste("/path/to/folder/overlap_beta_",Sys.Date(),".pdf",sep=""))
#pheatmap(beta_mat_df,cluster_method="Ward.D",clustering_distance_row ="euclidean" ,main=paste("Sample Overlap, beta"),treeheight_row=0, cluster_cols = FALSE,cluster_rows = FALSE, col= my_palette, breaks=bk, fontsize = 11,fontsize_row=10,show_rownames = TRUE, border_color = border_colours_beta)
#dev.off()


