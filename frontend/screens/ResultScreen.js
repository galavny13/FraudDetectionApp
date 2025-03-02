"use client"
import { View, StyleSheet, ScrollView } from "react-native"
import { useAppContext } from "../context/AppContext"
import { Text, Card, Icon, ListItem } from "@rneui/themed"

export default function ResultScreen() {
  const { analysisResult } = useAppContext()

  if (!analysisResult || !analysisResult.rows) {
    return (
      <View style={styles.container}>
        <Text>No analysis result available.</Text>
      </View>
    )
  }

  const fraudulentTransactions = analysisResult.rows.filter((row) => row.fraud_detected)

  return (
    <ScrollView contentContainerStyle={styles.container}>
      <Card containerStyle={styles.card}>
        <Card.Title>Analysis Result</Card.Title>
        <Card.Divider />
        <View style={styles.resultSummary}>
          <Icon
            name={fraudulentTransactions.length > 0 ? "warning" : "check-circle"}
            type="material"
            color={fraudulentTransactions.length > 0 ? "#ff6b6b" : "#51cf66"}
            size={40}
          />
          <Text style={styles.resultText}>
            {fraudulentTransactions.length > 0
              ? `${fraudulentTransactions.length} Fraudulent Transaction(s) Detected`
              : "No Fraudulent Transactions Detected"}
          </Text>
        </View>
      </Card>

      <Card containerStyle={styles.card}>
        <Card.Title>Transaction Details</Card.Title>
        <Card.Divider />
        {analysisResult.rows.map((transaction, index) => (
          <ListItem key={index} bottomDivider>
            <ListItem.Content>
              <ListItem.Title>{transaction.merchant}</ListItem.Title>
              <ListItem.Subtitle>
                {transaction.date} - {transaction.category}
              </ListItem.Subtitle>
              <Text>
                Amount: {transaction.currency} {transaction.amount}
              </Text>
              <Text>Type: {transaction.type}</Text>
              <Text style={transaction.fraud_detected ? styles.fraudDetected : styles.noFraud}>
                {transaction.explanation}
              </Text>
            </ListItem.Content>
          </ListItem>
        ))}
      </Card>
    </ScrollView>
  )
}

const styles = StyleSheet.create({
  container: {
    flexGrow: 1,
    padding: 20,
    backgroundColor: "#f6f6f6",
  },
  card: {
    borderRadius: 10,
    marginBottom: 20,
  },
  resultSummary: {
    flexDirection: "row",
    alignItems: "center",
    justifyContent: "center",
    marginBottom: 20,
  },
  resultText: {
    fontSize: 18,
    fontWeight: "bold",
    marginLeft: 10,
  },
  fraudDetected: {
    color: "#ff6b6b",
    fontWeight: "bold",
  },
  noFraud: {
    color: "#51cf66",
  },
})

