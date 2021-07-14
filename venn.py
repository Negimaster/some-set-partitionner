import sys

'''
Because Python's Sets are a pain with mutable objects or something, this projects uses lists as sets
I don't know how Python evaluates the `in` operator, if i'm unlucky, this code does not work
'''

class IdentifiedSet():
    '''
    Members:
        id: Unique id ( a string sounds nice )
        content: List of all elements
    '''

    def __init__(self, id, content=[]):
        '''
        Represents a set to be input into a Venn Diagramm

        Arguments:
            id: Unique id
            content: List of elements ( supposedly unique ) # TODO Check if duplicates exists ?
        '''

        self.id = id
        self.content = content.copy()

class VennPartition():
    '''
    Represent one partition in a Venn Diagramm

    Members:
        ids: List of the ids of the IdentifiedSets used to make this partition
             If there is only one id, this partition contains the elements that are unique to the IdentifiedSet of that id
             If there are two or more ids, this partition contains the set intersection of those IdentifiedSets

        content: List of elements ( supposedly unique ) taken from the IdentifiedSets with ids in self.ids
    '''

    def __init__(self, identifiedSet: IdentifiedSet):
        '''
        Initalizes VennPartition with an IdentifiedSet's members
        '''
        if identifiedSet != None:
            self.ids = [identifiedSet.id]
            self.content = identifiedSet.content.copy()
    
    def get_intersection_depth(self):
        '''
        Returns the number of IdentifiedSets used to make this partition
        '''
        return len(self.ids)

    def copy(self):
        new_partition = VennPartition(None)
        new_partition.ids = self.ids.copy()
        new_partition.content = self.content.copy()

        return new_partition

    def __id_already_exists(self, identifiedSet: IdentifiedSet):
        '''
        Checks whether or not the identifiedSet's id is already present/used in the ids

        Arguments:
            identifiedSet (IdentifiedSet): The IdentifiedSet to test

        Returns:
            (boolean) If the id is already present
        '''
        return identifiedSet.id in [id for id in self.ids]

    def __intersect_with(self, identifiedSet: IdentifiedSet):
        '''
        Modifies the VennPartition by intersecting with the new IdentifiedSet
        '''
        if self.__id_already_exists(identifiedSet):
            raise ValueError(f'Trying to intersect with IdentifiedSet with id {identifiedSet.id} but this id is already taken')

        self.ids.append(identifiedSet.id)
        self.content = [e for e in self.content if e in identifiedSet.content]

    def remove_elements(self, blacklist):
        '''
        Removes elements from self.content if it appears in content
        '''
        self.content = [e for e in self.content if e not in blacklist]
    
    def get_intersection_with(self, identifiedSet: IdentifiedSet):
        '''
        Creates the VennParition by intersecting the current elements list with the new IdentifiedSet
        '''
        if self.__id_already_exists(identifiedSet):
            raise ValueError(f'Trying to intersect with IdentifiedSet with id {identifiedSet.id} but this id is already taken')

        new_partition = self.copy()
        new_partition.__intersect_with(identifiedSet)
        return new_partition

class VennPartitioner():
    '''
    Main class that computes a Venn "Diagramm" iteratively from base IdentifiedSets

    Members:
        base_sets: List of all IdentifiedSet that served as a basis for the Venn diagramm
                   This will mostly be used by the user to know which VennPartition corresponds to which intersection of IdentifiedSet

        partitions: A List of List of VennPartition -> A representation by layers
                    The first layer contains VennPartitions of "exclusive elements" -> The elements that are unique to each base set
                    Layer i for i from 2 to N ( 1-based index ) contains the VennPartitions containing the intersections of i base sets
                    The last layer contains the intersection of all base sets

        global_union: The list of all elements
    '''

    def __init__(self):
        self.base_sets: list[IdentifiedSet] = []
        self.partitions: list[list[VennPartition]] = [[]]
        self.global_union = []

    def __identified_set_id_already_exists(self, identifiedSet: IdentifiedSet):
        '''
        Checks whether or not the identifiedSet's id is already present/used in the base_sets

        Arguments:
            identifiedSet (IdentifiedSet): The IdentifiedSet to test

        Returns:
            (boolean) If the id is already present
        '''
        return identifiedSet.id in [s.id for s in self.base_sets]

    def get_nb_base_sets(self):
        '''
        Returns:
            (int) Returns the current number of IdentifiedSet present in base_sets
        '''
        return len(self.base_sets)

    def __add_first_identified_set(self, identifiedSet: IdentifiedSet):
        '''
        Performs the first adding of an IdentifiedSet
        '''

        # Add VennPartition
        firstPartition = VennPartition(identifiedSet)
        self.partitions[-1].append(firstPartition)

        # Add elements to global union
        self.global_union.extend(identifiedSet.content)

        # Add IdentifiedSet to base set
        self.base_sets.append(identifiedSet)

    def __update_global_union(self, content):
        new_elements = [e for e in content if e not in self.global_union]
        self.global_union.extend(new_elements)

    def add_set(self, identifiedSet: IdentifiedSet):
        if self.__identified_set_id_already_exists(identifiedSet):
            raise ValueError(f'Trying to add IdentifiedSet with id {identifiedSet.id} but this id is already taken')

        if self.get_nb_base_sets() == 0:
            self.__add_first_identified_set(identifiedSet)
        else:

            # Add new global intersection
            old_global_intersection = self.partitions[-1][0] # There should be only one
            new_global_intersection = old_global_intersection.get_intersection_with(identifiedSet)
            self.partitions.append([new_global_intersection]) # This adds a new layer

            # Add 3-Set and higher intersections with the new IdentifiedSet
            # The upper bound has a -1 because we want to iterate on the old range
            for intersection_depth in range(2, len(self.partitions) - 1):
                new_intersections = [above_layer_set.get_intersection_with(identifiedSet) for above_layer_set in self.partitions[intersection_depth - 1]]
                self.partitions[intersection_depth - 1].extend(new_intersections)

            # Update exclusive Partitions
            for venn_partition in self.partitions[0]:
                venn_partition.remove_elements(identifiedSet.content)
            
            # Add new exclusive Partition
            new_exclusive_partition = VennPartition(identifiedSet)
            new_exclusive_partition.remove_elements(self.global_union)
            self.partitions[0].append(new_exclusive_partition)
                
            # Add new 2-Set intersections with the new IdentifiedSet
            new_partition = VennPartition(identifiedSet)
            new_2_sets_intersections = [new_partition.get_intersection_with(s) for s in self.base_sets]
            self.partitions[1].extend(new_2_sets_intersections)

            # Update global union
            self.__update_global_union(identifiedSet.content)

            # Add identifiedSet to base sets
            self.base_sets.append(identifiedSet)

def main(args):
    partitionner = VennPartitioner()

    # Create example IdentifiedSets
    set1 = IdentifiedSet('Set 1', ['a', 'b', 'c'])
    set2 = IdentifiedSet('Set 2', ['a', 'c'])
    set3 = IdentifiedSet('Set 3', ['b', 'c'])
    set4 = IdentifiedSet('Set 4', ['d', 'e'])

    # Add IdentifiedSets
    for s in [set1, set2, set3, set4]:
        partitionner.add_set(s)
    
    # Print partitions
    for layer in partitionner.partitions:
        for venn_partition in layer:
            if venn_partition.get_intersection_depth() == 1:
                print(f'Partition for elements exclusive to "{venn_partition.ids[0]}"')
                print(venn_partition.content)
            else:
                print(f'Partition for the intersections of {venn_partition.ids}')
                print(venn_partition.content)
            
            print()

if __name__ == '__main__':
    main(sys.argv[1:])