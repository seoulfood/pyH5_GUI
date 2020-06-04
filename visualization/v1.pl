#!/usr/bin/perl
use strict;
use warnings;
    
my $fileName = $ARGV[0];
my @classes;
my @definitions;
my @definitionsClasses;
my @classQueue;
my @defQueue;
my $lastClass;
my $lastDef;

open(my $pythonCode, '<:encoding(UTF-8)', $fileName)
    || die 'Could not open file $fileName';

while (my $row = <$pythonCode>){

    chomp $row;
    
    if($row =~ m/def\s+(.*)\s*\(.*\)/){
        $lastDef = $1;
        push @definitions, $lastDef;
        push @definitionsClasses, $lastClass;
        print "create($lastDef$lastClass:Subroutine{name:'$lastDef', file_name:'$fileName'})\n";
        print "create($lastDef$lastClass)-[:SUBROUTINE_OF]->($lastClass)\n";
    }
    if($row =~ m/class\s+(.*)\(.*\)\:/){
        $lastClass = $1;
        push @classes, $lastClass;
        print "create($lastClass:Class{name:'$lastClass', file_name:'$fileName'})\n";
    }
}

close $pythonCode;

my $currentSearch;
my $lineNumber;
my $classAssociation;
my $defNum = @definitions;

for(my $i = 0; $i < $defNum; $i++){
    $lineNumber = 0;
    $currentSearch = $definitions[$i];
    $classAssociation= $definitionsClasses[$i];

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
            print "create($currentSearch$classAssociation)-[:CALLED_BY{lineNumber:$lineNumber}]->($lastDef$lastClass)\n";
        }
        
        
    }

    close $pythonCode;
}
