import React, { useState, useEffect } from 'react';
import Box from '@mui/material/Box';
import Stepper from '@mui/material/Stepper';
import Step from '@mui/material/Step';
import StepLabel from '@mui/material/StepLabel';
import Button from '@mui/material/Button';
import Typography from '@mui/material/Typography';
import { AddPassengers } from './AddPassengers';
import { BookFlight } from './BookFlight';
import { Container } from '@mui/material';
import { useNavigate } from 'react-router'

const steps = ['Seleccionar asientos', '¿Quienes viajan?', 'Confirmar'];

export const BookFlightStepper = () => {
  const navigate = useNavigate();

  const [activeStep, setActiveStep] = React.useState(0);
  const [skipped, setSkipped] = React.useState(new Set());

  const [booking, setBooking] = useState({
    "selectedSeating": [[]],
    "passengers": [],
  });

  const isStepSkipped = (step) => {
    return skipped.has(step);
  };
  
  const handleNext = () => {
    let newSkipped = skipped;
    if (isStepSkipped(activeStep)) {
      newSkipped = new Set(newSkipped.values());
      newSkipped.delete(activeStep);
    }

    setActiveStep((prevActiveStep) => prevActiveStep + 1);
    setSkipped(newSkipped);
  };

  const handleBack = () => {
    setActiveStep((prevActiveStep) => prevActiveStep - 1);
  };

  const toHome = () => { navigate("/home") }

  return (
    <Container maxWidth="xl">
      <Box sx={{ width: '100%', marginTop: "40px"}}>
        <Stepper activeStep={activeStep}>
          {steps.map((label, index) => {
            const stepProps = {};
            const labelProps = {};
            if (isStepSkipped(index)) {
              stepProps.completed = false;
            }
            return (
              <Step key={label} {...stepProps}>
                <StepLabel {...labelProps}>{label}</StepLabel>
              </Step>
            );
          })}
        </Stepper>
        {activeStep === steps.length ? (
          <React.Fragment>
            <Typography sx={{ mt: 2, mb: 1 }}>
              Se realizo la reserva correctamente
            </Typography>
            <Box sx={{ display: 'flex', flexDirection: 'row', pt: 2 }}>
              <Box sx={{ flex: '1 1 auto' }} />
              <Button onClick={toHome}>Volver a inicio</Button>
            </Box>
          </React.Fragment>
        ) : (
          <React.Fragment>
            {
              (activeStep == 1)
              ?
              <AddPassengers booking={booking} setBooking={setBooking} />
              :
              (
                (activeStep == 2)
                ?
                <h1>Ultimo paso</h1>
                :
                <BookFlight booking={booking} setBooking={setBooking}/>
              )            
            }
            
            <Box sx={{ display: 'flex', flexDirection: 'row', pt: 2 }}>
              <Button
                color="inherit"
                disabled={activeStep === 0}
                onClick={handleBack}
                sx={{ mr: 1 }}
              >
                Atras
              </Button>

              <Box sx={{ flex: '1 1 auto' }} />

              <Button onClick={handleNext}>
                {activeStep === steps.length - 1 ? 'Confirmar' : 'Siguiente'}
              </Button>
            </Box>
          </React.Fragment>
        )}
      </Box>
    </Container>
  );
}