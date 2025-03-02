import { NavigationContainer } from "@react-navigation/native"
import { createStackNavigator } from "@react-navigation/stack"
import { AppProvider } from "./context/AppContext"
import HomeScreen from "./screens/HomeScreen"
import ResultScreen from "./screens/ResultScreen"
import { ThemeProvider, createTheme } from "@rneui/themed"
import { Image, View, Text } from "react-native"

const Stack = createStackNavigator()

const theme = createTheme({
  lightColors: {
    primary: "#003c42",
    secondary: "#dbcafe",
    background: "#f0f0f0",
  },
  mode: "light",
})

export default function App() {
  return (
    <ThemeProvider theme={theme}>
      <AppProvider>
        <NavigationContainer>
          <Stack.Navigator initialRouteName="Home">
            <Stack.Screen
              name="Home"
              component={HomeScreen}
              options={{
                headerTitle: () => (
                  <View style={{ flexDirection: "row", alignItems: "center" }}>
                    <Image
                      source={{
                        uri: "https://hebbkx1anhila5yf.public.blob.vercel-storage.com/logo-animation-new-0ntEkPNRwRT0uV6rT1qz6nHorfsdgY.png",
                      }}
                      style={{ width: 40, height: 40 }}
                      resizeMode="contain"
                    />
                    <Text style={{ marginLeft: 2, fontSize: 24, color: "#003c42" }}>Pyrite</Text>
                  </View>
                ),
                headerTitleAlign: "center",
                headerStyle: {
                  backgroundColor: "#f0f0f0",
                },
                headerTintColor: "#003c42",
              }}
            />
            <Stack.Screen
              name="Result"
              component={ResultScreen}
              options={{
                title: "Analysis Result",
                headerStyle: {
                  backgroundColor: "#f0f0f0",
                },
                headerTintColor: "#003c42",
              }}
            />
          </Stack.Navigator>
        </NavigationContainer>
      </AppProvider>
    </ThemeProvider>
  )
}

