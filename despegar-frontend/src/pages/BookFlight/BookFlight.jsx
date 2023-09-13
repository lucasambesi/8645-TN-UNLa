import React, { useState, useEffect } from "react";
import { styled } from "@mui/material/styles";
import Box from "@mui/material/Box";
import Paper from "@mui/material/Paper";
import Grid from "@mui/material/Grid";
import { Button, Chip, Container } from "@mui/material";
import { flightPresenter } from "../../presenter/FlightPresenter";
import HorizontalLinearStepper from "./BookStepper";
import { blueGrey } from "@mui/material/colors";

export const BookFlight = (props) => {
  const { getSeatingFlight } = flightPresenter();
  const [seating, setSeating] = useState([[]]);
  const [selectedSeating, setSelectedSeating] = useState([]);

  useEffect(() => {
    getSeatingFlight()
      .then((res) => {
        setSeating(res);
      })
      .catch((err) => console.log(err));
  }, []);

  function handleClick(rowIndex, columnIndex) {
    const newSeating = [...seating];
    const position = newSeating[rowIndex][columnIndex].position
    if(newSeating[rowIndex][columnIndex].status != 3){
      newSeating[rowIndex][columnIndex].status = 3;


      selectedSeating.push(position)

    }else{
      const newSelectedSeating  = selectedSeating.filter((post) => post !== position);
      setSelectedSeating(newSelectedSeating)

      newSeating[rowIndex][columnIndex].status = 1;
    }



    setSeating(newSeating);
  }

  function getColor(ubication) {
    if (ubication.status === 3) {
      return "#3cbabf";
    }

    return ubication.status === 1 ? "#19BA46" : "#808080";
  }

  return (
    <Container sx={{  marginTop: "2%"}}>

      <Box sx={{color:'purple'}}><h1 style={{ fontFamily: 'sans-serif',fontWeight: 700, letterSpacing: 3, color: 'purple'}}>Reserve sus asientos</h1></Box>
      
      <Grid container spacing={1}>
        {seating.map((array, rowIndex) => (
          <Box marginTop={rowIndex === 1 || rowIndex === 5 ? 5 : 1} key={rowIndex}>
            <Grid container item spacing={1}>
              {array.map((ubication, columnIndex) => (
                <Grid item key={columnIndex}>
                  <Box marginRight={columnIndex === 7 ? 5 : 0}>
                    <Chip
                      label={ubication.position}
                      disabled= {ubication.status == 2} 
                      onClick={ubication.status != 2 ? () => handleClick(rowIndex, columnIndex) : () => null}
                      sx={{
                        borderRadius: "0",
                        backgroundColor: getColor(ubication),
                        typography: "body2",
                        padding: 1,
                        textAlign: "center",
                        width: 60,
                      }}
                    />
                  </Box>
                </Grid>
              ))}
            </Grid>
          </Box>
        ))}
      </Grid>

      {/* <h5>Asientos selectionados:</h5>
      {selectedSeating.map((position, columnIndex) => (
          <body2>{position} </body2>
        ))} */}
      <Box sx={{  marginTop: "60px"}}><HorizontalLinearStepper ></HorizontalLinearStepper></Box>
    </Container>
    
  );

};