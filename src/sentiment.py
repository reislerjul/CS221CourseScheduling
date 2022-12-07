# Code adapted from https://github.com/Himabindugssn/Sentiment-classification-using-transformers

from tqdm import tqdm
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.utils.class_weight import compute_class_weight
from sklearn.metrics import classification_report
import torch
import torch.nn as nn
from torch.utils.data import TensorDataset, DataLoader, RandomSampler, SequentialSampler
from transformers import AdamW, AutoModel, BertTokenizerFast

device = torch.device("cuda")


LR = 1e-5  # Learning rate


class BERT_architecture(nn.Module):
    def __init__(self, bert):
        super(BERT_architecture, self).__init__()
        self.bert = bert
        # dropout layer
        self.dropout = nn.Dropout(0.2)
        # relu activation function
        self.relu = nn.ReLU()
        # dense layer 1
        self.fc1 = nn.Linear(768, 512)
        # dense layer 2 (Output layer)
        self.fc2 = nn.Linear(512, 5)  # 5 output classes
        self.softmax = nn.LogSoftmax(dim=1)

    # define the forward pass
    def forward(self, sent_id, mask):
        # pass the inputs to the model
        _, cls_hs = self.bert(sent_id, attention_mask=mask, return_dict=False)
        x = self.fc1(cls_hs)
        x = self.relu(x)
        x = self.dropout(x)
        # output layer
        x = self.fc2(x)
        # apply softmax activation
        x = self.softmax(x)
        return x


# function to train the model
def train(model, train_dataloader, cross_entropy, optimizer):
    model.train()

    total_loss, _ = 0, 0

    # empty list to save model predictions
    total_preds = []

    # iterate over batches
    for step, batch in tqdm(enumerate(train_dataloader)):

        # progress update after every 50 batches.
        if step % 50 == 0 and not step == 0:
            print("  Batch {:>5,}  of  {:>5,}.".format(step, len(train_dataloader)))

        # push the batch to gpu
        batch = [r.to(device) for r in batch]

        sent_id, mask, labels = batch

        # clear previously calculated gradients
        model.zero_grad()

        # get model predictions for the current batch
        preds = model(sent_id, mask)

        # compute the loss between actual and predicted values
        loss = cross_entropy(preds, labels)

        # add on to the total loss
        total_loss = total_loss + loss.item()

        # backward pass to calculate the gradients
        loss.backward()

        # clip the the gradients to 1.0. It helps in preventing the exploding gradient problem
        torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)

        # update parameters
        optimizer.step()

        # model predictions are stored on GPU. So, push it to CPU
        preds = preds.detach().cpu().numpy()

        # append the model predictions
        total_preds.append(preds)

    # compute the training loss of the epoch
    avg_loss = total_loss / len(train_dataloader)

    # predictions are in the form of (no. of batches, size of batch, no. of classes).
    # reshape the predictions in form of (number of samples, no. of classes)
    total_preds = np.concatenate(total_preds, axis=0)

    # returns the loss and predictions
    return avg_loss, total_preds


# function for evaluating the model
def evaluate(model, val_dataloader, cross_entropy):
    print("\nEvaluating...")

    # deactivate dropout layers
    model.eval()

    total_loss, _ = 0, 0

    # empty list to save the model predictions
    total_preds = []

    # iterate over batches
    for step, batch in tqdm(enumerate(val_dataloader)):

        # Progress update every 50 batches.
        if step % 50 == 0 and not step == 0:
            # # Calculate elapsed time in minutes.
            # elapsed = format_time(time.time() - t0)

            # Report progress.
            print("  Batch {:>5,}  of  {:>5,}.".format(step, len(val_dataloader)))

        # push the batch to gpu
        batch = [t.to(device) for t in batch]

        sent_id, mask, labels = batch

        # deactivate autograd
        with torch.no_grad():

            # model predictions
            preds = model(sent_id, mask)

            # compute the validation loss between actual and predicted values
            loss = cross_entropy(preds, labels)

            total_loss = total_loss + loss.item()

            preds = preds.detach().cpu().numpy()

            total_preds.append(preds)

    # compute the validation loss of the epoch
    avg_loss = total_loss / len(val_dataloader)
    # reshape the predictions in form of (number of samples, no. of classes)
    total_preds = np.concatenate(total_preds, axis=0)

    return avg_loss, total_preds


def run_bert(data, epochs, examples_set_aside, pad_len, lr=LR):
    data["Class"] = data["Label"].astype("int")
    data["Class"] = data["Class"] - 1  # n softmax values must be drawn from {0,..,n-1}

    # Drop reviews of more than 200 words, as there are a few outliers
    mask_lens = pd.DataFrame([len(str(i).split()) for i in data.Review])
    mask_lens.columns = ["length"]
    data = data.loc[mask_lens["length"] < 200]
    data = data.drop(columns=["CourseId", "Label"])

    data = data.dropna(axis=0, how="any")  # tokenizer requires no None reviews

    print(data.describe())
    data_reserve = data.sample(frac=examples_set_aside, axis=0)
    data = data.loc[~(data["Review"].isin(data_reserve["Review"]))]
    # Split into 70/15/15
    train_text, temp_text, train_labels, temp_labels = train_test_split(
        data["Review"],
        data["Class"],
        random_state=2021,
        test_size=0.3,
        stratify=data["Class"],
    )

    val_text, test_text, val_labels, test_labels = train_test_split(
        temp_text, temp_labels, random_state=2021, test_size=0.5, stratify=temp_labels
    )

    # import BERT-base pretrained model
    bert = AutoModel.from_pretrained("bert-base-uncased")  # This works

    # Load the BERT tokenizer
    tokenizer = BertTokenizerFast.from_pretrained("bert-base-uncased")  # This works

    tokens_train = tokenizer.batch_encode_plus(
        train_text.tolist(), max_length=pad_len, pad_to_max_length=True, truncation=True
    )
    tokens_val = tokenizer.batch_encode_plus(
        val_text.tolist(), max_length=pad_len, pad_to_max_length=True, truncation=True
    )
    tokens_test = tokenizer.batch_encode_plus(
        test_text.tolist(), max_length=pad_len, pad_to_max_length=True, truncation=True
    )
    train_seq = torch.tensor(tokens_train["input_ids"])
    train_mask = torch.tensor(tokens_train["attention_mask"])
    train_y = torch.tensor(train_labels.tolist())
    val_seq = torch.tensor(tokens_val["input_ids"])
    val_mask = torch.tensor(tokens_val["attention_mask"])
    val_y = torch.tensor(val_labels.tolist())
    test_seq = torch.tensor(tokens_test["input_ids"])
    test_mask = torch.tensor(tokens_test["attention_mask"])
    test_y = torch.tensor(test_labels.tolist())

    # define a batch size
    batch_size = 64

    # wrap tensors
    train_data = TensorDataset(train_seq, train_mask, train_y)
    # sampler for sampling the data during training
    train_sampler = RandomSampler(train_data)
    # dataLoader for train set
    train_dataloader = DataLoader(
        train_data, sampler=train_sampler, batch_size=batch_size
    )
    # wrap tensors
    val_data = TensorDataset(val_seq, val_mask, val_y)
    # sampler for sampling the data during training
    val_sampler = SequentialSampler(val_data)
    # dataLoader for validation set
    val_dataloader = DataLoader(val_data, sampler=val_sampler, batch_size=batch_size)

    # freeze the BERT architecture
    for param in bert.parameters():
        param.requires_grad = False

    # pass the pre-trained BERT to our define architecture
    model = BERT_architecture(bert)

    # push the model to GPU - I THINK DONT DO THIS
    model = model.to(device)

    # define the optimizer
    optimizer = AdamW(model.parameters(), lr=LR)  # learning rate

    # compute the class weights
    class_weights = compute_class_weight(
        class_weight="balanced", classes=np.unique(train_labels), y=train_labels
    )
    print("class weights are {} for {}".format(class_weights, np.unique(train_labels)))
    # count of both the categories of training labels
    print(pd.value_counts(train_labels))

    # wrap class weights in tensor
    weights = torch.tensor(class_weights, dtype=torch.float)

    # push weights to GPU -> SKIPPED
    weights = weights.to(device)

    # define loss function
    # add weights to handle the "imbalance" in the dataset
    cross_entropy = nn.NLLLoss(weight=weights)

    # avg_loss, total_preds = train(model, train_dataloader, cross_entropy, optimizer)

    # set initial loss to infinite
    best_valid_loss = float("inf")

    # empty lists to store training and validation loss of each epoch
    train_losses = []
    valid_losses = []

    # for each epoch
    for epoch in range(epochs):

        print("\n Epoch {:} / {:}".format(epoch + 1, epochs))

        # train model
        train_loss, _ = train(model, train_dataloader, cross_entropy, optimizer)

        # evaluate model
        valid_loss, _ = evaluate(model, val_dataloader, cross_entropy)

        # save the best model
        if valid_loss < best_valid_loss:
            best_valid_loss = valid_loss
            torch.save(model.state_dict(), "saved_weights.pt")

        # append training and validation loss
        train_losses.append(train_loss)
        valid_losses.append(valid_loss)

        print("\nTraining Loss: {}".format(train_loss))
        print("Validation Loss: {}".format(valid_loss))

    # load weights of best model
    path = "saved_weights.pt"
    model.load_state_dict(torch.load(path))

    # get predictions for test data
    with torch.no_grad():
        preds = model(test_seq.to(device), test_mask.to(device))
        # preds = model(test_seq, test_mask)
        preds = preds.detach().cpu().numpy()
    pred = np.argmax(preds, axis=1)
    print(classification_report(test_y, pred))
