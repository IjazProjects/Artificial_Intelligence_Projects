import sys
import random
import numpy as np
from collections import Counter

'''
For this assignment I used the slides from lecture which are called Decision Tree
and Practical Issues with Decision Tree. The pseducode from that was used for 
creating the DTL(), choose_attribute_optimized(), and choose_attribute_randomized(), 
and the details of that slide helped in creating this assignment

Here are the links:
    https://crystal.uta.edu/~gopikrishnav/classes/common/4308_5360/slides/08a_decision_trees.pdf
    https://crystal.uta.edu/~gopikrishnav/classes/common/4308_5360/slides/08b_decision_trees.pdf
'''

class TreeNode:
    def __init__(self, feature=None, threshold=None, left_child=None, right_child=None, is_leaf=False, class_label=None):
        '''
        Initializing the Tree Node attributes
        '''
        self.feature = feature
        self.threshold = threshold
        self.left_child = left_child
        self.right_child = right_child
        self.is_leaf = is_leaf
        self.class_label = class_label

class DecisionTree:

    def __init__(self, mode='optimized'):
        '''
        Initializing the Decision tree and the mode to choose the attribute
        '''
        self.root = None
        self.mode = mode
        
    def distribution(self, examples):
        '''
        Returning the distribution with the probbailities and label as a dictionary
        '''
        return {label: count / len(examples) for label, count in Counter(example[-1] for example in examples).items()} if examples else {}

    def build(self, examples, attributes):
        '''
        Starting the Decision Tree building process
        '''
        self.root = self.DTL(examples, attributes, None)

    def DTL(self, examples, attributes, default):
        '''
        Setting up the base cases for the recursive function
        '''
        if not examples:
            return TreeNode(is_leaf=True, class_label=default)
        elif all(example[-1] == examples[0][-1] for example in examples):
            return TreeNode(is_leaf=True, class_label=examples[0][-1])

        '''
        Will choose the right attribute function based on what mode the user has chose
        '''
        if self.mode == 'optimized':
            best_attribute, best_threshold = self.choose_attribute_optimized(examples, attributes)
        elif self.mode == 'randomized':
            best_attribute, best_threshold = self.choose_attribute_randomized(examples, attributes)

        '''
        Using the best attribute and best threshold that we got from the chosse
        attribute function we will split the examples
        '''
        examples_left = [example for example in examples if example[best_attribute] <= best_threshold]
        examples_right = [example for example in examples if example[best_attribute] > best_threshold]

        '''
        We will be pruning based on the the condition of having less than 50 examples
        we will remove that node and make the parent the new node
        '''
        if len(examples_left) < 50 or len(examples_right) < 50:
            most_common_label = Counter(example[-1] for example in examples).most_common(1)[0][0] if examples else None
            return TreeNode(is_leaf=True, class_label=most_common_label)

        '''
        Recursion starts here we will use this to build the tree
        '''
        tree = TreeNode(feature=best_attribute, threshold=best_threshold)
        tree.left_child = self.DTL(examples_left, attributes, self.distribution(examples_left))
        tree.right_child = self.DTL(examples_right, attributes, self.distribution(examples_right))

        return tree

    def choose_attribute_optimized(self, examples, attributes):
        '''
        Initialize the attribute, threhold, and gain. We will loop over all the
        attributes, finding the min and max of the attreibute and try 50 threshold
        values between them. We do so by calculating the information gain and 
        choosing the best attrribute and threshold based on that, and return it
        '''
        max_gain = -1
        best_attribute = None
        best_threshold = None
        for attribute in attributes:
            attribute_values = [example[attribute] for example in examples]
            L = min(attribute_values)
            M = max(attribute_values)
            for K in range(1, 51):
                threshold = L + K * (M - L) / 51
                gain = self.information_gain(examples, attribute, threshold)
                if gain > max_gain:
                    max_gain = gain
                    best_attribute = attribute
                    best_threshold = threshold

        return best_attribute, best_threshold

    def choose_attribute_randomized(self, examples, attributes):
        '''
        Initialize the attribute, threhold, and gain. We will find a random
        attribute rather than looping over all of it, finding the min and max 
        of the attribute and try 50 threshold values between them. We do so by 
        calculating the information gain and choosing the best attrribute and 
        threshold based on that, and return it.
        '''
        max_gain = -1
        best_threshold = None
        attribute = random.choice(attributes)  

        attribute_values = [example[attribute] for example in examples]
        L = min(attribute_values)
        M = max(attribute_values)

        for K in range(1, 51):
            threshold = L + K * (M - L) / 51
            gain = self.information_gain(examples, attribute, threshold)
            if gain > max_gain:
                max_gain = gain
                best_threshold = threshold

        return attribute, best_threshold


    def information_gain(self, examples, attribute, threshold):
        '''
        For all the splits we will call the entropy function to calculate the 
        weighted entropy and summing it for all the splits
        '''
        splits = [[], []]
        for ex in examples:
            splits[ex[attribute] > threshold].append(ex)

        weighted_entropy = sum((len(split) / len(examples)) * self.entropy(split) for split in splits)

        return self.entropy(examples) - weighted_entropy
    
    def entropy(self, examples):
        '''
        We will calculate the entropy for the information gain and return it
        '''
        label_counts = Counter(example[-1] for example in examples)
        probabilities = [count / len(examples) for count in label_counts.values()]
        return -sum(p * np.log2(p) for p in probabilities if p > 0)

    def predict(self, example):
        '''
        By checking the tree feature and threshold we will figure out if it is 
        the right or left child of the tree, and return its class label
        '''
        tree = self.root
        while not tree.is_leaf:
            tree = tree.left_child if example[tree.feature] <= tree.threshold else tree.right_child
        return tree.class_label


class DecisionForest:
    def __init__(self, num_trees):
        '''
        Creating n number of trees based on the user choice
        '''
        self.num_trees = num_trees
        self.trees = [DecisionTree(mode="randomized") for tree in range(num_trees)]

    def build(self, examples, attributes):
        
        '''
        We prepare the training data and send it to the decision tree class to
        build the trees in our decision forest
        '''
        training_data = [examples[i] + [attributes[i]] for i in range(len(attributes))]
        for tree in self.trees:
            tree.build(training_data, list(range(len(examples[0]))))

    def predict_forest(self, example):
        '''
        We call upon the decision tree predict functions for all our trees
        and get the top two most common due to determining if there is a tie,
        and if so we will return the predicted class, if there is a ties, and 
        the tied classes
        '''
        predictions = [tree.predict(example) for tree in self.trees]
        prediction_count = Counter(predictions)
        potential_tie = prediction_count.most_common(2)
        tie = len(potential_tie) == 2 and potential_tie[0][1] == potential_tie[1][1]
        
        return potential_tie[0][0], tie, [potential_tie[0][0], potential_tie[1][0]] if tie else None

    def calculate_accuracy(self, example, attributes):
        '''
        Processing the accuracy of the decision forest
        '''
        return (sum(self.predict_forest(example[i])[0] == attributes[i] for i in range(len(attributes)))) / len(attributes)
        

def data_processing(file_path):
    '''
    We will process both the training and test files and convert the strings
    into integers so we can do calculations later on and seperate the data into
    features and class labels
    '''
    data = []
    with open(file_path, 'r') as file:
        for line in file:
            data.append([int(float(value)) for value in line.split()])
            
    features = [value[:] for value in data]  
    labels = [value[-1] for value in data]    
   
    return features, labels

def main():
    '''
    Initializing the training and test file along with the option the user chooses
    '''
    if len(sys.argv) < 4:
        print("Please give correct command line parameters")
        sys.exit(0)
    
    training_file, test_file, option = sys.argv[1], sys.argv[2], sys.argv[3]
    
    '''
    We process the training and test files and set up the features and attributes
    '''
    train_features, train_labels = data_processing(training_file)
    test_features, test_labels = data_processing(test_file)
    num_features = len(train_features[0])
    attributes = list(range(num_features))  
    
    '''
    We call the decisonn tree or forest based on what the user has mentioned
    in the command line arguments
    '''
    if option == 'optimized' or option == 'randomized':
        tree = DecisionTree(mode=option)
        tree.build(train_features, attributes) 
    
    elif option == 'forest3':
        print("in forest3")
        forest = DecisionForest(num_trees=3)  
        forest.build(train_features, train_labels)
        forest_accuracy = forest.calculate_accuracy(train_features, train_labels)
        tree = forest
    
    elif option == 'forest15':
        print("in forest15")
        forest = DecisionForest(num_trees=15)  # Adjusted for random forest
        forest.build(train_features, train_labels)  # Calling build method here
        forest_accuracy = forest.calculate_accuracy(train_features, train_labels)
        tree = forest
        
    else:
        print("Invalid option. Choose from 'optimized', 'randomized', 'forest3', 'forest15'.")
        sys.exit(1)
    
    '''
    We will generate the output file with the correct format, and here we will 
    get the accuracy calculations ready based on whether it is a decision tree
    or decision forest such that we can account for ties.
    '''
    total_accuracy = 0
    with open('output.txt', 'w') as file:
        for i, test_instance in enumerate(test_features):
            predicted_class, is_tie, tied_classes = (tree.predict(test_instance), False, None) if option in ['optimized', 'randomized'] else tree.predict_forest(test_instance)
            true_class = test_labels[i]
            accuracy = 1 if predicted_class == true_class else 0
            if is_tie:
                accuracy = 1 / len(tied_classes) if true_class in tied_classes else 0
    
            total_accuracy += accuracy
            file.write(f"Object Index = {i}, Result = {predicted_class}, True Class = {true_class}, Accuracy = {accuracy}\n")
    
        overall_accuracy = total_accuracy / len(test_features)
        if option == 'optimized' or option == 'randomized':
            file.write(f"Classification Accuracy = {overall_accuracy}\n")
            print(f"Classification Accuracy = {overall_accuracy}")
        else:
            file.write(f"Classification Accuracy = {forest_accuracy}\n")
            print(f"Classification Accuracy = {forest_accuracy}\n")

if __name__ == "__main__":
    main()