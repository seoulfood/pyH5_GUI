#!/usr/bin/perl
use strict;
use warnings;
    
my $fileName;
my $fileNum = @ARGV;
my @classes;
my @definitions;
my @definitionsClasses;
my @classQueue;
my @defQueue;
my $lastClass;
my $lastDef;
my $tempFile = 'temp.txt';
my $pythonCode;
my $temp;

system('rm temp.txt');


foreach(@ARGV){
    $fileName = $_;
    print STDERR "$fileName\n";
   
    open($pythonCode, '<:encoding(UTF-8)', $fileName)
        || die 'Could not open file $fileName';

    open($temp, '>>', $tempFile)
        || die 'Could not open temp file $tempFile';

    while (my $row = <$pythonCode>){

        chomp $row;
    
        if($row =~ m/def\s+(.*)\s*\(.*\)/){
            $lastDef = $1;
            push @definitions, $lastDef;
            push @definitionsClasses, $lastClass;
            print $temp "create($lastDef$lastClass:Subroutine{name:'$lastDef', file_name:'$fileName'})\n";
            print $temp "create($lastDef$lastClass)-[:SUBROUTINE_OF]->($lastClass)\n";
        }
        if($row =~ m/class\s+(.*)\(.*\)\:/){
            $lastClass = $1;
            push @classes, $lastClass;
            print $temp "create($lastClass:Class{name:'$lastClass', file_name:'$fileName'})\n";
        }
    }

    close $pythonCode;
}

my $currentSearch;
my $lineNumber;
my $classAssociation;
my $defNum = @definitions;

for(my $i = 0; $i < $defNum; $i++){
    $lineNumber = 0;
    $currentSearch = $definitions[$i];
    $classAssociation= $definitionsClasses[$i];

    if($currentSearch eq '__init__'){next;}

    foreach(@ARGV){
        $fileName = $_;
        open($pythonCode, '<:encoding(UTF-8)', $fileName)
            || die 'Could not open file $fileName';
        
        while (my $row = <$pythonCode>){
            $lineNumber++;
            chomp $row;
            
            if($row =~ m/def\s+(.*)\(.*\)/){
                $lastDef=$1;
                next;
            }
            if($row =~ m/class\s+(.*)\(.*\)\:/){
                $lastClass=$1;
                next;
            }
            
            if($row =~ m/$currentSearch/){
                #print $temp "create($currentSearch$classAssociation)-[:CALLED_BY{lineNumber:$lineNumber}]->($lastDef$lastClass)\n";
                print $temp "create($currentSearch$classAssociation)-[:CALLED_BY]->($lastDef$lastClass)\n";
            }
            
            
        }
    
        close $pythonCode;
    }
}
my $duplicateRemoval = "awk '!_[\$0]++' temp.txt";
system($duplicateRemoval);
system('rm temp.txt');
close $temp;
