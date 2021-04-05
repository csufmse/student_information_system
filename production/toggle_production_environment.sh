# Set your environment file if different
ENV=".env"

if [[ -f $ENV ]]
then
    case $(grep PRODUCTION $ENV) in
    
        *True)
            sed -i -e '/PRODUCTION/s/True/False/' -i -e '/DEBUG/s/False/True/' $ENV
            ;;
        *False)
            sed -i -e '/PRODUCTION/s/False/True/' -i -e '/DEBUG/s/True/False/' $ENV
            ;;  
        *)
            echo "Something missing from the environment file. Make sure both PRODUCTION and DEBUG variables are present"
            ;;
    esac
else
    echo "No environment file found. Make sure your environment file is in the same directory as this executable and variable name is set correct."
fi
